import { useParams, useNavigate } from "react-router-dom";
import { mapDetails, mapsOutput } from "../data/demo";
import { PriorityBadge, StatusBadge, ImpactScore } from "../components/Badges";

function Section({ title, icon, accent = "#10b981", children }) {
  return (
    <div className="card" style={{ padding: 22, marginBottom: 14 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16, paddingBottom: 12, borderBottom: "1px solid rgba(255,255,255,0.05)" }}>
        <div style={{ width: 26, height: 26, borderRadius: 6, background: `${accent}18`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13 }}>{icon}</div>
        <span style={{ fontSize: 11, fontWeight: 700, color: "#475569", textTransform: "uppercase", letterSpacing: 0.7 }}>{title}</span>
      </div>
      {children}
    </div>
  );
}

export default function MapDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const detail   = mapDetails[id];
  const listItem = mapsOutput.find(m => m.map_id === id);

  if (!listItem) return (
    <div style={{ textAlign: "center", padding: 80 }}>
      <div style={{ fontSize: 44, marginBottom: 12 }}>📋</div>
      <div style={{ fontSize: 17, fontWeight: 700, color: "#94a3b8" }}>MAP not found</div>
      <button onClick={() => navigate("/maps")} style={{ marginTop: 16, padding: "10px 24px", background: "#10b981", color: "#fff", border: "none", borderRadius: 8, fontWeight: 700 }}>← Back to MAPs</button>
    </div>
  );

  const data = detail || {
    ...listItem,
    department: { name: listItem.department, confidence: 0.91, keywords: ["compliance","regulatory","risk"] },
    source_requirement: { req_id: "REQ-XXXX", text: "Detailed requirement text will be populated from the backend.", source_document: "RBI Circular", domain: "Compliance", subdomain: "General" },
    cross_references: [], related_maps: [],
  };

  const pColor = { Critical:"#f87171", High:"#fbbf24", Medium:"#60a5fa", Low:"#34d399" }[data.priority] || "#10b981";
  const isOverdue = listItem.deadline < new Date().toISOString().split("T")[0];

  return (
    <div className="animate-fade-in">
      <button onClick={() => navigate("/maps")} style={{
        background: "#1a2332", border: "1.5px solid rgba(255,255,255,0.08)", borderRadius: 7,
        padding: "8px 16px", fontSize: 12.5, color: "#94a3b8", fontWeight: 600,
        display: "inline-flex", alignItems: "center", gap: 6, marginBottom: 18,
        transition: "all 0.15s",
      }}
        onMouseEnter={e => { e.currentTarget.style.borderColor = "#10b981"; e.currentTarget.style.color = "#10b981"; }}
        onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.08)"; e.currentTarget.style.color = "#94a3b8"; }}
      >← Back to MAPs</button>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, marginBottom: 18 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
            <span style={{ fontFamily: "monospace", fontSize: 11.5, fontWeight: 800, color: "#34d399", background: "rgba(52,211,153,0.1)", padding: "3px 9px", borderRadius: 5, border: "1px solid rgba(52,211,153,0.2)" }}>{data.map_id}</span>
            <PriorityBadge priority={data.priority} size="lg" />
            <StatusBadge status={data.status} />
          </div>
          <h1 style={{ fontSize: 21, fontWeight: 800, color: "#f1f5f9", letterSpacing: -0.3, lineHeight: 1.35 }}>{data.title}</h1>
        </div>
        {/* Conic gauge */}
        <div style={{
          width: 84, height: 84, borderRadius: "50%", flexShrink: 0,
          background: `conic-gradient(${pColor} ${data.impact_score * 36}deg, #1a2332 0deg)`,
          display: "flex", alignItems: "center", justifyContent: "center",
          boxShadow: `0 0 20px ${pColor}28`,
        }}>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: "#1a2332", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
            <div style={{ fontSize: 18, fontWeight: 900, color: pColor, lineHeight: 1 }}>{data.impact_score.toFixed(1)}</div>
            <div style={{ fontSize: 8.5, color: "#475569", fontWeight: 600 }}>IMPACT</div>
          </div>
        </div>
      </div>

      {/* Section 1 */}
      <Section title="MAP Information" icon="📊" accent="#60a5fa">
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }}>
          {[
            { label: "PRIORITY",   value: <PriorityBadge priority={data.priority} /> },
            { label: "DEPARTMENT", value: <span style={{ fontSize: 13, fontWeight: 700, color: "#e2e8f0" }}>{data.department.name}</span> },
            { label: "DEADLINE",   value: <span style={{ fontSize: 13, fontWeight: 700, color: isOverdue ? "#f87171" : "#d1d5db" }}>{listItem.deadline}</span> },
            { label: "STATUS",     value: <StatusBadge status={data.status} /> },
          ].map(({ label, value }) => (
            <div key={label} style={{ background: "#162030", borderRadius: 8, padding: "10px 14px", border: "1px solid rgba(255,255,255,0.05)" }}>
              <div style={{ fontSize: 9.5, color: "#475569", fontWeight: 700, letterSpacing: 0.5, marginBottom: 6 }}>{label}</div>
              {value}
            </div>
          ))}
        </div>
      </Section>

      {/* Section 2 */}
      <Section title="Department Assignment" icon="🏛" accent="#a78bfa">
        <div style={{ display: "grid", gridTemplateColumns: "180px 1fr 1fr", gap: 20, alignItems: "start" }}>
          <div>
            <div style={{ fontSize: 10, color: "#475569", fontWeight: 700, marginBottom: 5 }}>ASSIGNED DEPARTMENT</div>
            <div style={{ fontSize: 14, fontWeight: 800, color: "#e2e8f0" }}>{data.department.name}</div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: "#475569", fontWeight: 700, marginBottom: 7 }}>CONFIDENCE SCORE</div>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ flex: 1, height: 8, background: "#162030", borderRadius: 4, overflow: "hidden" }}>
                <div style={{ width: `${(() => {
                  const conf = data.department.confidence > 1 ? data.department.confidence / 100 : data.department.confidence;
                  return conf * 100;
                })()}%`, height: "100%", background: "linear-gradient(90deg,#10b981,#34d399)", borderRadius: 4 }} />
              </div>
              <span style={{ fontSize: 14, fontWeight: 800, color: "#34d399" }}>{(() => {
                const conf = data.department.confidence > 1 ? data.department.confidence / 100 : data.department.confidence;
                return (conf * 100).toFixed(0);
              })()}%</span>
            </div>
          </div>
          <div>
            <div style={{ fontSize: 10, color: "#475569", fontWeight: 700, marginBottom: 7 }}>MATCHED KEYWORDS</div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
              {data.department.keywords.map(k => (
                <span key={k} style={{ background: "rgba(96,165,250,0.12)", color: "#93c5fd", padding: "3px 10px", borderRadius: 20, fontSize: 11.5, fontWeight: 700, border: "1px solid rgba(96,165,250,0.2)" }}>{k}</span>
              ))}
            </div>
          </div>
        </div>
      </Section>

      {/* Section 3 */}
      <Section title="Source Requirement" icon="📄" accent="#fbbf24">
        <div style={{ display: "flex", gap: 8, marginBottom: 14, flexWrap: "wrap" }}>
          {[["REQ ID", data.source_requirement.req_id, "#34d399"], ["SOURCE", data.source_requirement.source_document, "#d1d5db"], ["DOMAIN", data.source_requirement.domain, "#a78bfa"], ["SUBDOMAIN", data.source_requirement.subdomain, "#60a5fa"]].map(([lbl, val, c]) => (
            <div key={lbl} style={{ background: "#162030", border: "1px solid rgba(255,255,255,0.06)", borderRadius: 7, padding: "5px 12px" }}>
              <span style={{ fontSize: 9.5, color: "#475569", fontWeight: 700 }}>{lbl}: </span>
              <span style={{ fontSize: 12, fontWeight: 700, color: c }}>{val}</span>
            </div>
          ))}
        </div>
        <blockquote style={{
          margin: 0, padding: "16px 18px",
          background: "rgba(251,191,36,0.06)", borderLeft: "3px solid #fbbf24",
          borderRadius: "0 8px 8px 0", color: "#d1d5db", fontSize: 13.5, lineHeight: 1.8,
          border: "1px solid rgba(251,191,36,0.12)", borderLeft: "3px solid #fbbf24",
        }}>
          {data.source_requirement.text}
        </blockquote>
      </Section>

      {/* AI Reasoning (Explainability) */}
      <div className="card" style={{ padding: 22, marginBottom: 14, background: "rgba(96,165,250,0.04)", border: "1px solid rgba(96,165,250,0.15)" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 26, height: 26, borderRadius: 6, background: "rgba(96,165,250,0.15)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 13 }}>🧠</div>
            <span style={{ fontSize: 11, fontWeight: 800, color: "#60a5fa", textTransform: "uppercase", letterSpacing: 0.7 }}>AI ASSIGNMENT REASONING</span>
          </div>
          <button onClick={() => {
            const blob = new Blob([`MAP EXPORT\n\nID: ${data.map_id}\nTitle: ${data.title}\nPriority: ${data.priority}\nDepartment: ${data.department.name}\nDeadline: ${listItem.deadline}\n\nAI REASONING:\nThis MAP was generated with ${data.priority} priority because the source requirement (${data.source_requirement.req_id}) poses significant ${data.department.name} compliance risk.`], { type: "text/plain" });
            const url = URL.createObjectURL(blob); const a = document.createElement("a"); a.href = url; a.download = `MAP_${data.map_id}.txt`; a.click();
          }} style={{ padding: "5px 12px", background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)", borderRadius: 6, color: "#94a3b8", fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
            Export Report
          </button>
        </div>
        <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.6 }}>
          The RegIntel AI engine designated this MAP as <strong>{data.priority}</strong> priority with an impact score of <strong>{data.impact_score.toFixed(1)}</strong> because the source requirement (<strong>{data.source_requirement.req_id}</strong>) mandates immediate remediation under the <strong>{data.source_requirement.domain}</strong> framework. It was deterministically assigned to <strong>{data.department.name}</strong> due to a {data.department.confidence * 100}% confidence match with departmental keywords: {data.department.keywords.join(", ")}.
        </div>
      </div>

      {/* Sections 4 & 5 */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 14 }}>
        <Section title="Cross References" icon="🔗" accent="#60a5fa">
          {data.cross_references.length === 0
            ? <div style={{ color: "#475569", fontSize: 13, textAlign: "center", padding: "12px 0" }}>No cross-references available.</div>
            : data.cross_references.map((r, i) => (
              <div key={r.req_id} style={{ padding: "11px 13px", borderRadius: 7, marginBottom: 8, background: "#162030", borderLeft: "2px solid #60a5fa", transition: "transform 0.12s" }}
                onMouseEnter={e => e.currentTarget.style.transform = "translateX(3px)"}
                onMouseLeave={e => e.currentTarget.style.transform = "translateX(0)"}>
                <div style={{ fontSize: 10.5, fontWeight: 800, color: "#60a5fa", marginBottom: 4 }}>{r.req_id}</div>
                <div style={{ fontSize: 12.5, color: "#94a3b8", lineHeight: 1.6 }}>{r.text}</div>
              </div>
            ))}
        </Section>

        <Section title="Related MAPs" icon="🔄" accent="#a78bfa">
          {data.related_maps.length === 0
            ? <div style={{ color: "#475569", fontSize: 13, textAlign: "center", padding: "12px 0" }}>No related MAPs.</div>
            : data.related_maps.map(r => (
              <div key={r.map_id} onClick={() => navigate(`/maps/${r.map_id}`)}
                style={{ padding: "11px 13px", borderRadius: 7, marginBottom: 8, background: "#162030", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center", transition: "all 0.14s" }}
                onMouseEnter={e => { e.currentTarget.style.background = "rgba(167,139,250,0.08)"; e.currentTarget.style.transform = "translateX(3px)"; }}
                onMouseLeave={e => { e.currentTarget.style.background = "#162030"; e.currentTarget.style.transform = "translateX(0)"; }}>
                <div>
                  <div style={{ fontSize: 10.5, fontWeight: 800, color: "#a78bfa", marginBottom: 3 }}>{r.map_id}</div>
                  <div style={{ fontSize: 12.5, color: "#d1d5db", fontWeight: 500 }}>{r.title}</div>
                </div>
                <div style={{ display: "flex", gap: 7, alignItems: "center", flexShrink: 0 }}>
                  <PriorityBadge priority={r.priority} />
                  <span style={{ color: "#334155", fontSize: 16 }}>›</span>
                </div>
              </div>
            ))}
        </Section>
      </div>
    </div>
  );
}
