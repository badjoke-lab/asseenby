import React from "react";
import ReactDOM from "react-dom/client";
import "./styles.css";

const SUPPORT_URL = "https://buy.stripe.com/6oUcMY4cD3Zm6FdcNdcIE02?utm_source=asseenby&utm_medium=site&utm_campaign=support";

function SupportPage() {
  return (
    <div className="page-shell">
      <div className="page-frame">
        <header className="topbar">
          <a href="/" className="brand">AsSeenBy</a>
          <nav className="topnav">
            <a href="/">Home</a>
            <a href="/#workspace">Compare</a>
            <a href="/#modes">Modes</a>
            <a href="/support/">Support</a>
          </nav>
          <a href="/" className="ghost-button">Open viewer</a>
        </header>

        <main className="content-area support-page">
          <section className="support-hero">
            <div>
              <div className="support-kicker">Independent project support</div>
              <h1 className="support-title">Support AsSeenBy</h1>
            </div>
            <div className="support-copy">
              <p>
                AsSeenBy is an independent project focused on visual perception, accessibility, and research-oriented visual comparison.
              </p>
              <p>
                If the project is useful to you, you can support its maintenance, hosting, research, and future development.
              </p>
              <p>
                Support is optional. Every contribution helps keep the project online and supports future improvements.
              </p>
            </div>
          </section>

          <section className="support-grid">
            <article className="support-card">
              <div className="plate-title">What support helps with</div>
              <div className="support-list">
                <p>Ongoing maintenance and fixes</p>
                <p>Hosting and project operation</p>
                <p>Research, iteration, and future improvements</p>
              </div>
            </article>

            <article className="support-card support-card--action">
              <div className="plate-title">One-time support</div>
              <p className="support-action-copy">
                One-time support via Stripe in USD.
              </p>
              <a
                href={SUPPORT_URL}
                target="_blank"
                rel="noopener noreferrer"
                className="primary-button support-button"
              >
                Support AsSeenBy
              </a>
              <p className="support-note">
                Thank you for supporting independent work.
              </p>
            </article>
          </section>
        </main>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("support-root")!).render(
  <React.StrictMode>
    <SupportPage />
  </React.StrictMode>,
);
