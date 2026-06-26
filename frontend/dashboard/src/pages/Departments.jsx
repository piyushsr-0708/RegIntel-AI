import { departmentSummary, departmentHeatmap } from "../data/demo";
import { useLocation, useParams, useNavigate } from "react-router-dom";
import { useAnalysisSession } from "../context/AnalysisSession";
import Breadcrumbs from "../components/Breadcrumbs";

const RISK_COLOR = (s) => s >= 85 ? "#f87171" : s >= 70 ? "#fbbf24" : s >= 55 ? "#60a5fa" : "#34d399";
const HEAT = {
  Critical: { r: 239, g: 68,  b: 68  },
  High:     { r: 251, g: 191, b: 36  },
  Medium:   { r: 96,  g: 165, b: 250 },
  Low:      { r: 52,  g: 211, b: 153 },
};

function heatBg(col, val) {
  const { r, g, b } = HEAT[col];
  return `rgba(${r},${g},${b},${Math.min(0.08 + val * 0.09, 0.85)})`;
}

function ScopedDepartmentReport({ deptId }) {
  const { session, downloadReport } = useAnalysisSession();
  const navigate = useNavigate();
  const decodedDept = decodeURIComponent(deptId);
  const deptData = session?.analysis?.departments?.find(d => d.department === decodedDept);

  if (!deptData) return <div style={{ color: "#f87171", padding: 20 }}>Department data not found in current analysis session.</div>;

  const relevantMaps = session.analysis.maps.filter(m => m.department === decodedDept);
  const criticalMaps = relevantMaps.filter(m => m.priority === "Critical");
  const upcomingMaps = relevantMaps.filter(m => m.priority === "Critical" || m.priority === "High").slice(0, 3);
  const estimatedWorkload = deptData.total_maps * 8.5; // deterministic dummy

  return (
    <div className="animate-fade-in">
      <Breadcrumbs />
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#10b981,#059669)", boxShadow: "0 0 10px rgba(16,185,129,0.4)" }} />
            <h1 className="page-title">Department Action Center</h1>
          </div>
          <p className="page-subtitle" style={{ paddingLeft: 14 }}>
            Action plan for <strong style={{ color: "#f1f5f9" }}>{decodedDept}</strong> based on {session.file.name}
          </p>
        </div>
        <div style={{ display: "flex", gap: 12 }}>
          <button onClick={() => downloadReport("Department", deptData)} style={{ padding: "8px 18px", borderRadius: 8, background: "rgba(96,165,250,0.12)", border: "1px solid rgba(96,165,250,0.3)", color: "#93c5fd", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
            Export Report
          </button>
          <button onClick={() => window.location.href = "/departments"} style={{ padding: "8px 18px", borderRadius: 8, background: "rgba(52,211,153,0.12)", border: "1px solid rgba(52,211,153,0.3)", color: "#6ee7b7", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
            View Global Dashboard
          </button>
        </div>
      </div>

      {/* AI Recommendation */}
      <div className="card" style={{ padding: "20px 24px", marginBottom: 16, background: "linear-gradient(135deg, rgba(16,185,129,0.08) 0%, #1a2332 100%)", borderLeft: "4px solid #10b981" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
          <div style={{ width: 26, height: 26, borderRadius: 6, background: "rgba(16,185,129,0.15)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13 }}>🧠</div>
          <span style={{ fontSize: 11, fontWeight: 800, color: "#34d399", textTransform: "uppercase", letterSpacing: 0.7 }}>AI ASSIGNMENT REASONING & RECOMMENDATION</span>
        </div>
        <div style={{ fontSize: 13.5, color: "#e2e8f0", lineHeight: 1.6 }}>
          RegIntel AI successfully mapped <strong>{relevantMaps.length}</strong> requirements from <em>{session.file.name}</em> directly to the <strong>{decodedDept}</strong> department with a confidence score of {deptData.confidence}. 
          <br/><br/>
          <strong>Next Action:</strong> You have {deptData.Critical} Critical tasks that pose an immediate risk of non-compliance. Prioritize allocating resources to these action plans within the next 14 days. The total estimated workload for this compliance effort is {estimatedWorkload} person-hours.
        </div>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Workload and Progress */}
        <div className="card" style={{ padding: "24px 28px" }}>
          <div style={{ fontSize: 15, fontWeight: 800, color: "#f1f5f9", marginBottom: 16 }}>Workload & Progress</div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
            {[
              ["Total Tasks", deptData.total_maps, "#a78bfa"],
              ["Critical", deptData.Critical, "#ef4444"],
              ["Completion Status", "0%", "#94a3b8"],
              ["Est. Workload", `${estimatedWorkload} hrs`, "#fbbf24"],
            ].map(([label, val, color]) => (
              <div key={label} style={{ padding: "12px", background: "#162030", borderRadius: 8, textAlign: "center", border: `1px solid ${color}20` }}>
                <div style={{ fontSize: 22, fontWeight: 900, color, lineHeight: 1 }}>{val}</div>
                <div style={{ fontSize: 10, color: "#64748b", marginTop: 4, fontWeight: 600 }}>{label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Immediate Tasks */}
        <div className="card" style={{ padding: "24px 28px" }}>
          <div style={{ fontSize: 15, fontWeight: 800, color: "#f1f5f9", marginBottom: 16 }}>Immediate Action Required</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {upcomingMaps.length > 0 ? upcomingMaps.map(m => (
              <div key={m.map_id} onClick={() => navigate(`/maps/${m.map_id}`)} style={{ padding: "12px 14px", background: "#162030", borderRadius: 8, borderLeft: `3px solid ${m.priority === "Critical" ? "#ef4444" : "#fbbf24"}`, cursor: "pointer" }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontSize: 11, fontWeight: 800, color: m.priority === "Critical" ? "#ef4444" : "#fbbf24" }}>{m.priority}</span>
                  <span style={{ fontSize: 11, color: "#94a3b8", fontFamily: "monospace" }}>{m.map_id}</span>
                </div>
                <div style={{ fontSize: 13, color: "#e2e8f0", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{m.title}</div>
              </div>
            )) : <div style={{ color: "#94a3b8", fontSize: 13 }}>No immediate tasks assigned.</div>}
          </div>
          <button onClick={() => navigate("/pipeline/analysis/maps")} style={{ width: "100%", marginTop: 14, padding: "8px", borderRadius: 6, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.25)", color: "#34d399", fontSize: 11.5, fontWeight: 700, cursor: "pointer" }}>
            View All {deptData.total_maps} Action Plans →
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Departments() {
  const maxScore = Math.max(...departmentSummary.map(d => d.total_risk_score));
  const { pathname } = useLocation();
  const { deptId } = useParams();
  
  if (pathname.includes("/pipeline/analysis/department/") && deptId) {
    return <ScopedDepartmentReport deptId={deptId} />;
  }

  return (
    <div>
      <div className="page-header">
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
          <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#f87171,#ef4444)", boxShadow: "0 0 10px rgba(239,68,68,0.4)" }} />
          <h1 className="page-title">Department Risk Dashboard</h1>
        </div>
        <p className="page-subtitle" style={{ paddingLeft: 14 }}>
          Compliance burden across <strong style={{ color: "#f1f5f9" }}>{departmentSummary.length}</strong> departments · {departmentSummary.reduce((a, d) => a + d.total_maps, 0)} total MAPs
        </p>
      </div>

      {/* Top 3 Alert Cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 14, marginBottom: 20 }}>
        {departmentSummary.slice(0, 3).map((d, i) => {
          const color = RISK_COLOR(d.total_risk_score);
          return (
            <div key={d.department} style={{
              borderRadius: 12, padding: "18px 20px", position: "relative", overflow: "hidden",
              background: "#1a2332", border: `1px solid ${color}25`,
              boxShadow: `0 4px 20px ${color}12`,
            }}>
              <div style={{ position: "absolute", top: -8, right: -8, fontSize: 68, opacity: 0.04, fontWeight: 900, color }}>#{i + 1}</div>
              <div style={{ display: "flex", alignItems: "center", gap: 7, marginBottom: 11 }}>
                <span style={{ width: 7, height: 7, borderRadius: "50%", background: color, display: "inline-block", animation: "pulse-dot 2s ease infinite" }} />
                <span style={{ fontSize: 10, fontWeight: 700, color, letterSpacing: 0.5 }}>#{i + 1} HIGHEST RISK</span>
              </div>
              <div style={{ fontSize: 14, fontWeight: 800, color: "#f1f5f9", marginBottom: 14, lineHeight: 1.3 }}>{d.department}</div>
              <div style={{ display: "flex", gap: 18 }}>
                {[["Risk Score", d.total_risk_score, color], ["Critical MAPs", d.critical_count, "#f87171"], ["Total MAPs", d.total_maps, "#94a3b8"]].map(([lbl, val, c]) => (
                  <div key={lbl}>
                    <div style={{ fontSize: 24, fontWeight: 900, color: c, lineHeight: 1 }}>{val}</div>
                    <div style={{ fontSize: 10, color: "#475569", marginTop: 2 }}>{lbl}</div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Bar Chart — pure SVG, zero hover */}
      <div className="card" style={{ padding: "22px 20px", marginBottom: 18 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 18 }}>
          <div>
            <div style={{ fontWeight: 700, color: "#f1f5f9", fontSize: 14 }}>Department Risk Ranking</div>
            <div style={{ fontSize: 11.5, color: "#64748b", marginTop: 2 }}>All 12 departments ranked by composite risk score</div>
          </div>
          <div style={{ display: "flex", gap: 12 }}>
            {[["#f87171","85+"],["#fbbf24","70+"],["#60a5fa","55+"],["#34d399","Low"]].map(([c, l]) => (
              <div key={l} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11 }}>
                <div style={{ width: 8, height: 8, borderRadius: 2, background: c }} />
                <span style={{ color: "#64748b" }}>{l}</span>
              </div>
            ))}
          </div>
        </div>
        <svg width="100%" height={320} viewBox="0 0 600 320" preserveAspectRatio="xMinYMin meet" style={{ display: "block", pointerEvents: "none" }}>
          {departmentSummary.map((d, i) => {
            const labelW = 160, barH = 18, gap = 8, top = 6;
            const rowH = barH + gap;
            const y = top + i * rowH;
            const maxW = 380;
            const barW = (d.total_risk_score / 100) * maxW;
            const color = RISK_COLOR(d.total_risk_score);
            return (
              <g key={d.department}>
                <text x={0} y={y + barH / 2 + 4} fontSize={10.5} fill="#94a3b8">{d.department}</text>
                <rect x={labelW} y={y} width={Math.max(barW, 4)} height={barH} rx={4} fill={color} opacity={0.8} />
                <text x={labelW + barW + 6} y={y + barH / 2 + 4} fontSize={10.5} fill="#64748b" fontWeight="700">{d.total_risk_score}</text>
              </g>
            );
          })}
        </svg>
      </div>

      {/* Heatmap */}
      <div className="card" style={{ padding: 22, marginBottom: 18 }}>
        <div style={{ fontWeight: 700, color: "#f1f5f9", fontSize: 14, marginBottom: 4 }}>Priority Heatmap</div>
        <div style={{ fontSize: 11.5, color: "#64748b", marginBottom: 16 }}>MAP counts by department and priority level</div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "separate", borderSpacing: "3px", minWidth: 520 }}>
            <thead>
              <tr>
                <th style={{ padding: "7px 12px", textAlign: "left", fontSize: 11, color: "#475569", fontWeight: 700 }}>Department</th>
                {["Critical","High","Medium","Low"].map((p) => (
                  <th key={p} style={{ padding: "7px 14px", textAlign: "center", fontSize: 11, fontWeight: 700, color: { Critical: "#f87171", High: "#fbbf24", Medium: "#60a5fa", Low: "#34d399" }[p] }}>{p}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {departmentHeatmap.map((row) => (
                <tr key={row.department}>
                  <td style={{ padding: "5px 12px", fontSize: 12.5, color: "#94a3b8", fontWeight: 500, whiteSpace: "nowrap" }}>{row.department}</td>
                  {["Critical","High","Medium","Low"].map((p) => {
                    const v = row[p];
                    return (
                      <td key={p} style={{ padding: "4px 14px", textAlign: "center" }}>
                        <div style={{
                          display: "inline-flex", alignItems: "center", justifyContent: "center",
                          minWidth: 38, height: 34, borderRadius: 7,
                          background: heatBg(p, v),
                          fontWeight: 800, fontSize: 14,
                          color: v >= 6 ? "#fff" : { Critical: "#f87171", High: "#fbbf24", Medium: "#60a5fa", Low: "#34d399" }[p],
                        }}>{v}</div>
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Cards */}
      <div style={{ fontSize: 10.5, fontWeight: 700, color: "#475569", letterSpacing: 0.6, textTransform: "uppercase", marginBottom: 10 }}>All Departments</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 12 }}>
        {departmentSummary.map((d) => {
          const color = RISK_COLOR(d.total_risk_score);
          return (
            <div key={d.department} className="card" style={{ padding: "16px 18px", borderLeft: `3px solid ${color}` }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0", marginBottom: 12 }}>{d.department}</div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 10 }}>
                {[["Total MAPs", d.total_maps, "#94a3b8"], ["Risk Score", d.total_risk_score, color], ["Critical", d.critical_count, "#f87171"]].map(([lbl, val, c]) => (
                  <div key={lbl} style={{ textAlign: "center" }}>
                    <div style={{ fontSize: 22, fontWeight: 900, color: c, lineHeight: 1 }}>{val}</div>
                    <div style={{ fontSize: 10, color: "#475569", marginTop: 2 }}>{lbl}</div>
                  </div>
                ))}
              </div>
              <div style={{ height: 3, background: "#162030", borderRadius: 2, overflow: "hidden" }}>
                <div style={{ width: `${(d.total_risk_score / maxScore) * 100}%`, height: "100%", background: color }} />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
