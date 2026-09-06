import fs from "node:fs/promises";

const beforePath = process.argv[2] || "r12-resolution-before.json";
const afterPath = process.argv[3] || "r12-resolution-after.json";
const before = JSON.parse(await fs.readFile(beforePath, "utf8"));
const after = JSON.parse(await fs.readFile(afterPath, "utf8"));

function assert(condition, message) {
  if (!condition) throw new Error(message);
}

function key(row) {
  return `${row.mode}:${row.strength}`;
}

const beforeRows = new Map(before.rows.map((row) => [key(row), row]));
const afterRows = new Map(after.rows.map((row) => [key(row), row]));
assert(beforeRows.size === 10 && afterRows.size === 10, `expected 10 audit rows before/after; got ${beforeRows.size}/${afterRows.size}`);

let beforeMeanSum = 0;
let afterMeanSum = 0;
const comparisons = [];

for (const [rowKey, prior] of beforeRows) {
  const current = afterRows.get(rowKey);
  assert(current, `missing normalized row ${rowKey}`);
  beforeMeanSum += prior.meanChannelError;
  afterMeanSum += current.meanChannelError;

  const ratio = prior.meanChannelError > 0 ? current.meanChannelError / prior.meanChannelError : 0;
  const improvedEnough = current.meanChannelError <= Math.max(1.5, prior.meanChannelError * 0.75);
  const notLocallyWorse = current.p95ChannelError <= Math.max(8, prior.p95ChannelError + 1);
  const absoluteMeanOk = current.meanChannelError <= 6.0;

  comparisons.push({
    key: rowKey,
    beforeMean: prior.meanChannelError,
    afterMean: current.meanChannelError,
    meanRatio: Number(ratio.toFixed(3)),
    beforeP95: prior.p95ChannelError,
    afterP95: current.p95ChannelError,
  });

  console.log(
    `R12 A/B ${rowKey}: mean ${prior.meanChannelError} -> ${current.meanChannelError} ` +
    `(ratio ${ratio.toFixed(3)}), p95 ${prior.p95ChannelError} -> ${current.p95ChannelError}`,
  );

  assert(absoluteMeanOk, `${rowKey}: normalized mean remains too resolution-dependent (${current.meanChannelError})`);
  assert(improvedEnough, `${rowKey}: normalized mean did not improve enough (${prior.meanChannelError} -> ${current.meanChannelError})`);
  assert(notLocallyWorse, `${rowKey}: p95 became materially worse (${prior.p95ChannelError} -> ${current.p95ChannelError})`);
}

const beforeAverage = beforeMeanSum / beforeRows.size;
const afterAverage = afterMeanSum / afterRows.size;
console.log(`R12 aggregate mean error: ${beforeAverage.toFixed(3)} -> ${afterAverage.toFixed(3)} (${(afterAverage / beforeAverage).toFixed(3)}x)`);
assert(afterAverage <= beforeAverage * 0.55, `aggregate cross-resolution error did not fall by at least 45% (${beforeAverage} -> ${afterAverage})`);

await fs.writeFile(
  "r12-resolution-comparison.json",
  JSON.stringify({ beforeAverage, afterAverage, comparisons }, null, 2),
);
