import { lazy, Suspense } from "react";
import App from "./App";
import "./spatial.css";

const SpatialPage = lazy(() => import("./SpatialPage"));

export default function ExperienceRoot() {
  const pathname = typeof window !== "undefined"
    ? window.location.pathname.replace(/\/+$/, "") || "/"
    : "/";
  const view = typeof window !== "undefined"
    ? new URLSearchParams(window.location.search).get("view")
    : null;

  if (pathname === "/" && view === "spatial") {
    return (
      <Suspense fallback={<SpatialLoading />}>
        <SpatialPage />
      </Suspense>
    );
  }

  if (pathname === "/support") {
    return <App />;
  }

  return (
    <>
      <nav className="experience-switch" aria-label="AsSeenBy experience">
        <span className="experience-switch__label">Experience</span>
        <a className="experience-switch__link experience-switch__link--active" href="/" aria-current="page">
          Compare image
        </a>
        <a className="experience-switch__link" href="/?view=spatial">
          Explore 3D
        </a>
      </nav>
      <App />
    </>
  );
}

function SpatialLoading() {
  return (
    <div className="page-shell">
      <div className="page-frame">
        <main className="content-area" role="status" aria-live="polite">
          <p>Loading spatial viewer…</p>
        </main>
      </div>
    </div>
  );
}
