import App from "./App";
import SpatialPage from "./SpatialPage";
import "./spatial.css";

export default function ExperienceRoot() {
  const pathname = typeof window !== "undefined"
    ? window.location.pathname.replace(/\/+$/, "") || "/"
    : "/";

  if (pathname === "/spatial") {
    return <SpatialPage />;
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
        <a className="experience-switch__link" href="/spatial/">
          Explore 3D
        </a>
      </nav>
      <App />
    </>
  );
}
