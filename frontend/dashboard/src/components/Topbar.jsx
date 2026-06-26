import { NavLink } from "react-router-dom";
import { useContext } from "react";
import { DemoContext } from "../App";

const NAV = [
  { to: "/", label: "Dashboard", icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg> },
  { to: "/pipeline", label: "Pipeline", icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path d="M9 10l3 3-3 3M15 10v6"/></svg> },
  { to: "/maps", label: "MAP Management", icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/><line x1="9" y1="12" x2="15" y2="12"/><line x1="9" y1="16" x2="13" y2="16"/></svg> },
  { to: "/departments", label: "Department Risk", icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><path d="M3 21h18M9 21V7l3-4 3 4v14M9 12h6"/></svg> },
  { to: "/requirements", label: "Requirements", icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg> },
  { to: "/graph", label: "Knowledge Graph", icon: <svg width="15" height="15" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg> },
];

export default function Topbar() {
  const { isDemo, toggleDemo } = useContext(DemoContext);
  return (
    <header style={{
      position: "sticky", top: 0, zIndex: 100,
      background: "#0f1923",
      borderBottom: "1px solid rgba(16,185,129,0.15)",
      boxShadow: "0 2px 20px rgba(0,0,0,0.35)",
    }}>
      <div style={{ maxWidth: 1400, margin: "0 auto", padding: "0 32px", display: "flex", alignItems: "center", height: 60 }}>
        {/* Brand */}
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginRight: 40, flexShrink: 0 }}>
          <div style={{
            width: 32, height: 32, borderRadius: 8,
            background: "linear-gradient(135deg,#10b981,#059669)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 0 14px rgba(16,185,129,0.45)",
          }}>
            <svg width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="#fff" strokeWidth="2.5">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <div style={{ color: "#f8fafc", fontWeight: 800, fontSize: 13.5, letterSpacing: 0.2, lineHeight: 1 }}>RegIntel AI</div>
            <div style={{ color: "#10b981", fontSize: 9.5, fontWeight: 700, letterSpacing: 1, lineHeight: 1, marginTop: 2 }}>Agentic Regulatory Intelligence & Compliance Platform</div>
          </div>
        </div>

        {/* Nav */}
        <nav style={{ display: "flex", alignItems: "center", gap: 2, flex: 1 }}>
          {NAV.map(({ to, label, icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              style={({ isActive }) => ({
                display: "flex", alignItems: "center", gap: 7,
                padding: "7px 14px", borderRadius: 7,
                textDecoration: "none",
                color: isActive ? "#10b981" : "rgba(148,163,184,0.8)",
                background: isActive ? "rgba(16,185,129,0.12)" : "transparent",
                border: isActive ? "1px solid rgba(16,185,129,0.2)" : "1px solid transparent",
                fontSize: 13, fontWeight: isActive ? 700 : 500,
                transition: "all 0.15s",
                whiteSpace: "nowrap",
              })}
              onMouseEnter={(e) => {
                if (!e.currentTarget.style.color.includes("16,185,129") && !e.currentTarget.style.color.includes("10b981")) {
                  e.currentTarget.style.color = "#e2e8f0";
                  e.currentTarget.style.background = "rgba(255,255,255,0.05)";
                }
              }}
              onMouseLeave={(e) => {
                const isActive = e.currentTarget.getAttribute("aria-current") === "page";
                if (!isActive) {
                  e.currentTarget.style.color = "rgba(148,163,184,0.8)";
                  e.currentTarget.style.background = "transparent";
                }
              }}
            >
              <span style={{ opacity: 0.85, flexShrink: 0 }}>{icon}</span>
              {label}
            </NavLink>
          ))}
        </nav>

        {/* Live badge & Demo toggle */}
        <div style={{ display: "flex", alignItems: "center", gap: 14, marginLeft: 20, flexShrink: 0 }}>
          <button onClick={toggleDemo} title="Toggle Demo Mode" style={{
            display: "flex", alignItems: "center", gap: 6,
            background: isDemo ? "rgba(139,92,246,0.15)" : "transparent",
            border: `1px solid ${isDemo ? "rgba(139,92,246,0.4)" : "rgba(255,255,255,0.1)"}`,
            color: isDemo ? "#c4b5fd" : "#94a3b8",
            borderRadius: 20, padding: "5px 12px", fontSize: 11, fontWeight: 700, transition: "all 0.2s",
            cursor: "pointer"
          }}>
            <span style={{ display: "inline-block", width: 8, height: 8, borderRadius: "50%", background: isDemo ? "#8b5cf6" : "#475569", boxShadow: isDemo ? "0 0 8px #8b5cf6" : "none" }} />
            DEMO
          </button>
          
          <div style={{
            display: "flex", alignItems: "center", gap: 6,
            background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)",
            borderRadius: 20, padding: "5px 12px",
          }}>
            <span style={{ width: 6, height: 6, borderRadius: "50%", background: "#10b981", display: "inline-block", animation: "pulse-dot 2s ease-in-out infinite" }} />
            <span style={{ color: "#10b981", fontSize: 11, fontWeight: 700, letterSpacing: 0.3 }}>LIVE</span>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: "#94a3b8" }}>
              {new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
