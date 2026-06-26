import { NavLink, useLocation } from "react-router-dom";

const CRUMB_MAP = {
  "/": "Dashboard",
  "/pipeline": "Pipeline",
  "/maps": "MAP Management",
  "/departments": "Department Risk",
  "/requirements": "Requirements",
  "/graph": "Knowledge Graph",
};

export default function Breadcrumbs() {
  const { pathname } = useLocation();
  const segments = pathname.split("/").filter(Boolean);

  // Build crumbs
  const crumbs = [{ label: "Dashboard", path: "/" }];

  if (segments[0] === "pipeline") {
    crumbs.push({ label: "Pipeline", path: "/pipeline" });
    if (segments[1] === "analysis") {
      crumbs.push({ label: "Analysis", path: "/pipeline" });
      if (segments[2] === "maps") crumbs.push({ label: "Document MAPs", path: "/pipeline/analysis/maps" });
      else if (segments[2] === "graph") crumbs.push({ label: "Document Graph", path: "/pipeline/analysis/graph" });
      else if (segments[2] === "department" && segments[3]) crumbs.push({ label: decodeURIComponent(segments[3]), path: pathname });
    }
  } else if (segments[0]) {
    const label = CRUMB_MAP[`/${segments[0]}`] || segments[0];
    crumbs.push({ label, path: `/${segments[0]}` });
    if (segments[1]) crumbs.push({ label: segments[1], path: pathname });
  }

  if (crumbs.length <= 1) return null;

  return (
    <nav style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 20, fontSize: 12, flexWrap: "wrap" }}>
      {crumbs.map((c, i) => (
        <span key={c.path} style={{ display: "flex", alignItems: "center", gap: 6 }}>
          {i > 0 && <span style={{ color: "#334155" }}>›</span>}
          {i < crumbs.length - 1 ? (
            <NavLink to={c.path} style={{ color: "#64748b", textDecoration: "none", fontWeight: 600, transition: "color 0.15s" }}
              onMouseEnter={e => e.currentTarget.style.color = "#94a3b8"}
              onMouseLeave={e => e.currentTarget.style.color = "#64748b"}>
              {c.label}
            </NavLink>
          ) : (
            <span style={{ color: "#f1f5f9", fontWeight: 700 }}>{c.label}</span>
          )}
        </span>
      ))}
    </nav>
  );
}
