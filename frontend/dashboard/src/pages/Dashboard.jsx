import { useEffect, useState, useContext } from "react";
import { DemoContext } from "../App";
import { dashboardMetrics } from "../data/demo";
import { useAnalysisSession } from "../context/AnalysisSession";
import { useNavigate } from "react-router-dom";

const DONUT_COLORS = ["#ef4444", "#fbbf24", "#60a5fa", "#34d399"];

function useCountUp(target, duration = 1000) {
  const [count, setCount] = useState(0);
  useEffect(() => {
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= target) { setCount(target); clearInterval(timer); }
      else setCount(Math.floor(start));
    }, 16);
    return () => clearInterval(timer);
  }, [target, duration]);
  return count;
}

function KpiCard({ label, value, sub, icon, accent, delay = 0 }) {
  const count = useCountUp(value);
  return (
    <div className="card animate-fade-up" style={{ padding: "22px 22px", animationDelay: `${delay}ms`, position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: 2, background: accent }} />
      <div style={{ position: "absolute", top: 18, right: 18, width: 38, height: 38, borderRadius: 9, background: `${accent}18`, display: "flex", alignItems: "center", justifyContent: "center" }}>
        {icon}
      </div>
      <div style={{ fontSize: 32, fontWeight: 900, color: "#f1f5f9", letterSpacing: -1, lineHeight: 1, marginBottom: 7 }}>{count.toLocaleString()}</div>
      <div style={{ fontSize: 12.5, fontWeight: 700, color: "#94a3b8", marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 11, color: "#475569" }}>{sub}</div>
    </div>
  );
}

export default function Dashboard() {
  const m = dashboardMetrics;
  const { isDemo } = useContext(DemoContext);
  const { session, hasSession } = useAnalysisSession();
  const navigate = useNavigate();

  const kpis = [
    { label: "Total Requirements", value: m.total_requirements, sub: "Extracted from RBI Circulars", accent: "#60a5fa", icon: <svg width="18" height="18" fill="none" stroke="#60a5fa" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg> },
    { label: "Total MAPs Generated", value: m.total_maps, sub: "Mitigation Action Plans", accent: "#a78bfa", icon: <svg width="18" height="18" fill="none" stroke="#a78bfa" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg> },
    { label: "Critical MAPs", value: m.critical_maps, sub: "Immediate action required", accent: "#ef4444", icon: <svg width="18" height="18" fill="none" stroke="#ef4444" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg> },
    { label: "High Priority MAPs", value: m.high_priority_maps, sub: "Due within 90 days", accent: "#fbbf24", icon: <svg width="18" height="18" fill="none" stroke="#fbbf24" strokeWidth="2" viewBox="0 0 24 24"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg> },
    { label: "Departments Impacted", value: m.departments_impacted, sub: "Across the institution", accent: "#34d399", icon: <svg width="18" height="18" fill="none" stroke="#34d399" strokeWidth="2" viewBox="0 0 24 24"><path d="M3 21h18M9 21V7l3-4 3 4v14"/></svg> },
    { label: "Upcoming Deadlines", value: m.upcoming_deadlines, sub: "Within next 30 days", accent: "#fb923c", icon: <svg width="18" height="18" fill="none" stroke="#fb923c" strokeWidth="2" viewBox="0 0 24 24"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg> },
  ];

  const priorityData = Object.entries(m.priority_distribution).map(([name, value]) => ({ name, value }));
  const barColors = ["#ef4444", "#fbbf24", "#60a5fa", "#60a5fa", "#34d399"];
  const pieColors = ["#ef4444", "#fbbf24", "#60a5fa", "#34d399"];
  const pieTotal = priorityData.reduce((s, d) => s + d.value, 0);

  const complianceData = [
    { label: "Pending",     value: m.compliance_summary.pending,     color: "#94a3b8", icon: "○" },
    { label: "In Progress", value: m.compliance_summary.in_progress,  color: "#60a5fa", icon: "◑" },
    { label: "Completed",   value: m.compliance_summary.completed,    color: "#34d399", icon: "●" },
    { label: "Overdue",     value: m.compliance_summary.overdue,      color: "#ef4444", icon: "⚠" },
  ];

  return (
    <div>
      <div className="page-header" style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#10b981,#059669)", boxShadow: "0 0 10px rgba(16,185,129,0.5)" }} />
            <h1 className="page-title">Executive Dashboard</h1>
          </div>
          <p className="page-subtitle" style={{ paddingLeft: 14 }}>RBI Compliance Intelligence · Real-time Regulatory Analytics</p>
        </div>
        <div style={{ background: "#1a2332", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 9, padding: "9px 16px", textAlign: "right" }}>
          <div style={{ fontSize: 9.5, color: "#475569", fontWeight: 700, letterSpacing: 0.5 }}>LAST UPDATED</div>
          <div style={{ fontSize: 12.5, fontWeight: 700, color: "#f1f5f9", marginTop: 2 }}>{new Date().toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" })}</div>
          <div style={{ fontSize: 10, color: "#10b981", marginTop: 1, fontWeight: 700 }}>● Live</div>
        </div>
      </div>

      {hasSession && (
        <div className="card animate-fade-down" style={{ padding: "18px 24px", marginBottom: 22, background: "linear-gradient(135deg, rgba(139,92,246,0.1) 0%, rgba(139,92,246,0.02) 100%)", borderLeft: "4px solid #8b5cf6", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <div style={{ fontSize: 11, color: "#c4b5fd", fontWeight: 700, letterSpacing: 0.5, marginBottom: 4 }}>CURRENT ANALYSIS SESSION</div>
            <div style={{ fontSize: 16, fontWeight: 800, color: "#f1f5f9", marginBottom: 6 }}>{session.file.name}</div>
            <div style={{ display: "flex", gap: 16, fontSize: 12, color: "#94a3b8" }}>
              <span><strong style={{ color: "#e2e8f0" }}>{session.analysis.stats.totalRequirements}</strong> Requirements</span>
              <span><strong style={{ color: "#e2e8f0" }}>{session.analysis.stats.totalMaps}</strong> MAPs</span>
              <span><strong style={{ color: "#e2e8f0" }}>{session.analysis.stats.departmentsImpacted}</strong> Departments</span>
              <span>Processing Time: <strong style={{ color: "#10b981" }}>{(session.processing.totalElapsed / 1000).toFixed(1)}s</strong></span>
            </div>
          </div>
          <button onClick={() => navigate("/pipeline")} style={{ padding: "10px 20px", borderRadius: 8, background: "#8b5cf6", color: "#fff", border: "none", fontSize: 13, fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 14px rgba(139,92,246,0.4)" }}>
            Return to Analysis →
          </button>
        </div>
      )}

      {/* System Status and KPIs */}
      <div key={isDemo ? "demo" : "norm"} style={{ display: "grid", gridTemplateColumns: "1fr 2fr", gap: 14, marginBottom: 22 }}>
        {/* System Status Panel */}
        <div className="card animate-fade-up" style={{ padding: 22 }}>
          <div style={{ fontWeight: 700, color: "#f1f5f9", fontSize: 14, marginBottom: 16 }}>System Status</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {[
              { name: "Requirement Engine", status: isDemo ? "PROCESSING" : "READY" },
              { name: "Knowledge Graph", status: "READY" },
              { name: "Department Mapper", status: "READY" },
              { name: "MAP Generator", status: isDemo ? "PROCESSING" : "READY" },
              { name: "Dashboard Feed", status: "READY" }
            ].map(sys => (
              <div key={sys.name} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "8px 12px", background: "#162030", borderRadius: 8, border: "1px solid rgba(255,255,255,0.04)" }}>
                <span style={{ fontSize: 12, color: "#94a3b8", fontWeight: 600 }}>{sys.name}</span>
                <span style={{ fontSize: 10, fontWeight: 800, padding: "3px 8px", borderRadius: 12, background: sys.status === "READY" ? "rgba(16,185,129,0.15)" : "rgba(251,191,36,0.15)", color: sys.status === "READY" ? "#34d399" : "#fbbf24", border: `1px solid ${sys.status === "READY" ? "rgba(16,185,129,0.3)" : "rgba(251,191,36,0.3)"}` }}>
                  {sys.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* KPIs */}
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 14 }}>
          {kpis.map((k, i) => <KpiCard key={k.label} {...k} delay={i * 55} />)}
        </div>
      </div>

      {/* Charts */}
      <div key={`charts-${isDemo ? "demo" : "norm"}`} style={{ display: "grid", gridTemplateColumns: "1.1fr 0.9fr", gap: 16, marginBottom: 18 }}>
        {/* Bar — pure SVG, zero hover */}
        <div className="card animate-fade-up" style={{ padding: "22px 20px", animationDelay: "330ms" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
            <div>
              <div style={{ fontWeight: 700, color: "#f1f5f9", fontSize: 14 }}>Top Departments by Risk</div>
              <div style={{ fontSize: 11.5, color: "#64748b", marginTop: 2 }}>Composite risk scoring across all MAPs</div>
            </div>
            <span style={{ background: "rgba(239,68,68,0.12)", color: "#f87171", fontSize: 10.5, fontWeight: 700, padding: "3px 9px", borderRadius: 20, border: "1px solid rgba(239,68,68,0.2)" }}>HIGH RISK</span>
          </div>
          <svg width="100%" height={230} style={{ display: "block", pointerEvents: "none" }}>
            {m.top_risk_departments.map((d, i) => {
              const labelW = 138, barH = 20, gap = 26, top = 10;
              const y = top + i * (barH + gap);
              const barW = (d.risk_score / 100) * (560 - labelW - 30);
              return (
                <g key={d.department}>
                  <text x={0} y={y + barH / 2 + 4} fontSize={11} fill="#94a3b8">{d.department}</text>
                  <rect x={labelW} y={y} width={Math.max(barW, 4)} height={barH} rx={5} fill={barColors[i] || "#60a5fa"} opacity={0.85} />
                  <text x={labelW + barW + 6} y={y + barH / 2 + 4} fontSize={11} fill="#64748b" fontWeight="700">{d.risk_score}</text>
                </g>
              );
            })}
          </svg>
        </div>

        {/* Donut — pure SVG, zero hover */}
        <div className="card animate-fade-up" style={{ padding: "22px 20px", animationDelay: "390ms" }}>
          <div style={{ marginBottom: 14 }}>
            <div style={{ fontWeight: 700, color: "#f1f5f9", fontSize: 14 }}>Priority Distribution</div>
            <div style={{ fontSize: 11.5, color: "#64748b", marginTop: 2 }}>All {m.total_maps} MAPs by urgency</div>
          </div>
          <svg width="100%" height={210} viewBox="0 0 300 210" style={{ display: "block", pointerEvents: "none" }}>
            {(() => {
              const cx = 100, cy = 105, ro = 80, ri = 52;
              let angle = -Math.PI / 2;
              return priorityData.map((d, i) => {
                const slice = (d.value / pieTotal) * 2 * Math.PI;
                const x1 = cx + ro * Math.cos(angle), y1 = cy + ro * Math.sin(angle);
                const x2 = cx + ro * Math.cos(angle + slice), y2 = cy + ro * Math.sin(angle + slice);
                const ix1 = cx + ri * Math.cos(angle), iy1 = cy + ri * Math.sin(angle);
                const ix2 = cx + ri * Math.cos(angle + slice), iy2 = cy + ri * Math.sin(angle + slice);
                const large = slice > Math.PI ? 1 : 0;
                const mid = angle + slice / 2;
                const lx = cx + 62 * Math.cos(mid), ly = cy + 62 * Math.sin(mid);
                const path = `M${x1},${y1} A${ro},${ro} 0 ${large},1 ${x2},${y2} L${ix2},${iy2} A${ri},${ri} 0 ${large},0 ${ix1},${iy1} Z`;
                angle += slice;
                return (
                  <g key={d.name}>
                    <path d={path} fill={pieColors[i]} />
                    <text x={lx} y={ly + 4} textAnchor="middle" fontSize={11} fontWeight="700" fill="#fff">{d.value}</text>
                  </g>
                );
              });
            })()}
            {priorityData.map((d, i) => (
              <g key={d.name}>
                <rect x={200} y={40 + i * 28} width={10} height={10} rx={2} fill={pieColors[i]} />
                <text x={216} y={40 + i * 28 + 9} fontSize={11.5} fill="#94a3b8">{d.name} ({d.value})</text>
              </g>
            ))}
          </svg>
        </div>
      </div>

      {/* Compliance */}
      <div key={`comp-${isDemo ? "demo" : "norm"}`} className="card animate-fade-up" style={{ padding: 22, animationDelay: "450ms" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
          <div>
            <div style={{ fontWeight: 700, color: "#f1f5f9", fontSize: 14 }}>Compliance Summary</div>
            <div style={{ fontSize: 11.5, color: "#64748b", marginTop: 2 }}>Status across all {m.total_maps} MAPs</div>
          </div>
          <div style={{ fontSize: 12, color: "#34d399", fontWeight: 700 }}>{((m.compliance_summary.completed / m.total_maps) * 100).toFixed(0)}% completion rate</div>
        </div>
        <div style={{ height: 6, borderRadius: 3, background: "#162030", overflow: "hidden", display: "flex", marginBottom: 18 }}>
          {complianceData.map(({ value, color }) => (
            <div key={color} style={{ width: `${(value / m.total_maps) * 100}%`, background: color }} />
          ))}
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 12 }}>
          {complianceData.map(({ label, value, color, icon }) => (
            <div key={label} style={{ padding: "16px 14px", borderRadius: 9, background: "#162030", border: `1px solid ${color}22`, position: "relative", overflow: "hidden" }}>
              <div style={{ position: "absolute", bottom: -6, right: 2, fontSize: 46, opacity: 0.05, lineHeight: 1 }}>{icon}</div>
              <div style={{ fontSize: 32, fontWeight: 900, color, lineHeight: 1 }}>{value}</div>
              <div style={{ fontSize: 12, color: "#64748b", fontWeight: 600, marginTop: 5 }}>{label}</div>
              <div style={{ marginTop: 8, height: 3, borderRadius: 2, background: `${color}22`, overflow: "hidden" }}>
                <div style={{ width: `${(value / m.total_maps) * 100}%`, height: "100%", background: color }} />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
