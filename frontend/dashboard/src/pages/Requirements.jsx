import React, { useState, useMemo } from "react";
import { requirementsTaxonomy } from "../data/demo";

const DOMAINS = [...new Set(requirementsTaxonomy.map(r => r.domain))].sort();
const QUICK   = ["AML","STR","KYC","Wire Transfer","Sanctions","Due Diligence","Cybersecurity"];

const DM = {
  AML:             { accent: "#f87171", bg: "rgba(239,68,68,0.1)",  border: "rgba(239,68,68,0.22)" },
  KYC:             { accent: "#60a5fa", bg: "rgba(96,165,250,0.1)", border: "rgba(96,165,250,0.22)" },
  STR:             { accent: "#fbbf24", bg: "rgba(251,191,36,0.1)", border: "rgba(251,191,36,0.22)" },
  "Wire Transfer": { accent: "#34d399", bg: "rgba(52,211,153,0.1)", border: "rgba(52,211,153,0.2)" },
  Sanctions:       { accent: "#a78bfa", bg: "rgba(167,139,250,0.1)", border: "rgba(167,139,250,0.2)" },
  "Due Diligence": { accent: "#38bdf8", bg: "rgba(56,189,248,0.1)", border: "rgba(56,189,248,0.2)" },
  Cybersecurity:   { accent: "#fb923c", bg: "rgba(251,146,60,0.1)", border: "rgba(251,146,60,0.2)" },
};
const dm = (d) => DM[d] || { accent: "#94a3b8", bg: "rgba(148,163,184,0.08)", border: "rgba(148,163,184,0.15)" };

function highlight(text, query) {
  if (!query) return text;
  const parts = text.split(new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")})`, "gi"));
  return parts.map((p, i) =>
    p.toLowerCase() === query.toLowerCase()
      ? <mark key={i} style={{ background: "rgba(251,191,36,0.25)", color: "#fcd34d", borderRadius: 2, padding: "0 1px" }}>{p}</mark>
      : p
  );
}

const inp = { background: "#162030", border: "1.5px solid rgba(255,255,255,0.07)", borderRadius: 8, padding: "9px 13px", fontSize: 13, color: "#e2e8f0", transition: "border-color 0.15s, box-shadow 0.15s" };

const RequirementCard = React.memo(({ r, query, m, i }) => {
  const [expanded, setExpanded] = useState(false);
  
  return (
    <div className="card" style={{
      padding: "18px 20px", marginBottom: 10,
      borderLeft: `3px solid ${m.accent}`,
      animation: "fadeUp 0.32s ease both", animationDelay: `${i * 35}ms`,
      transition: "transform 0.14s, box-shadow 0.14s",
    }}
      onMouseEnter={e => { e.currentTarget.style.transform = "translateX(4px)"; e.currentTarget.style.boxShadow = "0 4px 20px rgba(0,0,0,0.35)"; }}
      onMouseLeave={e => { e.currentTarget.style.transform = "translateX(0)"; e.currentTarget.style.boxShadow = ""; }}
    >
      <div style={{ display: "flex", gap: 8, marginBottom: 11, flexWrap: "wrap", alignItems: "center" }}>
        <span style={{ fontFamily: "monospace", fontSize: 11, fontWeight: 800, color: "#34d399", background: "rgba(52,211,153,0.1)", padding: "3px 9px", borderRadius: 5, border: "1px solid rgba(52,211,153,0.18)" }}>{r.req_id}</span>
        <span style={{ fontSize: 11, fontWeight: 700, padding: "3px 10px", borderRadius: 20, background: m.bg, color: m.accent, border: `1px solid ${m.border}` }}>● {r.domain}</span>
        <span style={{ fontSize: 11, color: "#64748b", background: "#162030", padding: "3px 10px", borderRadius: 10, border: "1px solid rgba(255,255,255,0.05)" }}>{r.subdomain}</span>
        <span style={{ fontSize: 10.5, color: "#475569", marginLeft: "auto", display: "flex", alignItems: "center", gap: 4 }}>
          <svg width="11" height="11" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          {r.source_document}
        </span>
      </div>
      <p style={{ margin: 0, fontSize: 13.5, color: "#94a3b8", lineHeight: 1.75 }}>{highlight(r.text, query)}</p>
      
      <div style={{ display: "flex", justifyContent: "flex-end", marginTop: 12 }}>
        <button onClick={() => setExpanded(!expanded)} style={{ background: "transparent", border: "1px solid rgba(255,255,255,0.1)", color: "#94a3b8", fontSize: 11, fontWeight: 700, padding: "5px 12px", borderRadius: 6, cursor: "pointer", transition: "all 0.2s" }} onMouseEnter={e => e.currentTarget.style.color="#f1f5f9"} onMouseLeave={e => e.currentTarget.style.color="#94a3b8"}>
          {expanded ? "Hide Traceability ↑" : "Trace Lifecycle ↓"}
        </button>
      </div>

      {expanded && (
        <div className="animate-fade-in" style={{ marginTop: 14, paddingTop: 14, borderTop: "1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ fontSize: 11, color: "#475569", fontWeight: 700, marginBottom: 8, letterSpacing: 0.5 }}>COMPLIANCE LIFECYCLE TIMELINE</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 12, alignItems: "center", fontSize: 11, color: "#64748b", fontFamily: "monospace" }}>
            <span style={{ padding: "4px 8px", background: "#162030", borderRadius: 4, border: "1px solid rgba(255,255,255,0.05)" }}>Circular Parsed</span> <span style={{color: "#334155"}}>→</span>
            <span style={{ padding: "4px 8px", background: "#162030", borderRadius: 4, border: "1px solid rgba(255,255,255,0.05)", color: "#f1f5f9" }}>Extracted</span> <span style={{color: "#334155"}}>→</span>
            <span style={{ padding: "4px 8px", background: "#162030", borderRadius: 4, border: "1px solid rgba(255,255,255,0.05)", color: m.accent }}>{r.domain} Assigned</span> <span style={{color: "#334155"}}>→</span>
            <span style={{ padding: "4px 8px", background: "rgba(16,185,129,0.1)", borderRadius: 4, border: "1px solid rgba(16,185,129,0.2)", color: "#34d399" }}>MAP Generated</span> <span style={{color: "#334155"}}>→</span>
            <span style={{ padding: "4px 8px", background: "rgba(251,191,36,0.1)", borderRadius: 4, border: "1px solid rgba(251,191,36,0.2)", color: "#fbbf24" }}>Deadline Set</span>
          </div>

          <div style={{ marginTop: 14, padding: "12px 16px", background: "rgba(96,165,250,0.06)", border: "1px solid rgba(96,165,250,0.15)", borderRadius: 8 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, color: "#60a5fa", fontWeight: 800, marginBottom: 6, letterSpacing: 0.5 }}>
              <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M12 2v20m-7-7h14m-10-6h6"/></svg>
              AI TRACEABILITY & REASONING
            </div>
            <div style={{ fontSize: 12, color: "#e2e8f0", lineHeight: 1.6 }}>
              This requirement was deterministically mapped to the <strong>{r.domain}</strong> domain due to strong semantic proximity with existing regulatory heuristics. The system identified an explicit obligation under <strong>{r.subdomain}</strong> and successfully branched a Mitigation Action Plan to the responsible department to ensure timeline compliance.
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

export default function Requirements() {
  const [query, setQuery]   = useState("");
  const [domain, setDomain] = useState("");
  const [page, setPage]     = useState(1);
  const itemsPerPage = 50;

  const results = useMemo(() => {
    const q = query.toLowerCase();
    return requirementsTaxonomy.filter(r =>
      (!q || r.text.toLowerCase().includes(q) || r.req_id.toLowerCase().includes(q) || r.domain.toLowerCase().includes(q) || r.subdomain.toLowerCase().includes(q)) &&
      (!domain || r.domain === domain)
    );
  }, [query, domain]);

  const domainCounts = DOMAINS.map(d => ({ d, count: requirementsTaxonomy.filter(r => r.domain === d).length }));

  return (
    <div>
      <div className="page-header">
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
          <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#38bdf8,#0ea5e9)", boxShadow: "0 0 10px rgba(56,189,248,0.4)" }} />
          <h1 className="page-title">Requirement Search</h1>
        </div>
        <p className="page-subtitle" style={{ paddingLeft: 14 }}>
          <strong style={{ color: "#f1f5f9" }}>{requirementsTaxonomy.length}</strong> RBI compliance requirements across <strong style={{ color: "#f1f5f9" }}>{DOMAINS.length}</strong> regulatory domains
        </p>
      </div>

      {/* Domain pills */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 18 }}>
        {domainCounts.map(({ d, count }) => {
          const m = dm(d);
          const active = domain === d;
          return (
            <button key={d} onClick={() => { setDomain(active ? "" : d); setPage(1); }} style={{
              display: "flex", alignItems: "center", gap: 6, padding: "6px 13px",
              background: active ? m.bg : "#1a2332",
              border: `1.5px solid ${active ? m.accent : "rgba(255,255,255,0.07)"}`,
              borderRadius: 30, cursor: "pointer", transition: "all 0.15s",
            }}>
              <span style={{ width: 6, height: 6, borderRadius: "50%", background: m.accent, display: "inline-block" }} />
              <span style={{ fontSize: 12, fontWeight: 700, color: active ? m.accent : "#94a3b8" }}>{d}</span>
              <span style={{ fontSize: 10.5, fontWeight: 700, color: active ? m.accent : "#475569", background: active ? m.bg : "#162030", padding: "1px 6px", borderRadius: 10, border: `1px solid ${active ? m.border : "rgba(255,255,255,0.05)"}` }}>{count}</span>
            </button>
          );
        })}
      </div>

      {/* Search */}
      <div className="card" style={{ padding: "18px 22px", marginBottom: 16 }}>
        <div style={{ position: "relative", marginBottom: 13 }}>
          <svg style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", opacity: 0.3 }} width="16" height="16" fill="none" stroke="#94a3b8" strokeWidth="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input value={query} onChange={e => { setQuery(e.target.value); setPage(1); }}
            placeholder="Search by keyword, REQ ID, domain, subdomain…"
            style={{ ...inp, width: "100%", paddingLeft: 40, fontSize: 14, padding: "12px 40px 12px 40px" }}
            onFocus={e => { e.target.style.borderColor = "#10b981"; e.target.style.boxShadow = "0 0 0 3px rgba(16,185,129,0.1)"; }}
            onBlur={e  => { e.target.style.borderColor = "rgba(255,255,255,0.07)"; e.target.style.boxShadow = "none"; }}
          />
          {query && <button onClick={() => { setQuery(""); setPage(1); }} style={{ position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)", background: "rgba(255,255,255,0.08)", border: "none", borderRadius: "50%", width: 20, height: 20, color: "#94a3b8", fontSize: 11, display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>}
        </div>
        <div style={{ display: "flex", gap: 7, flexWrap: "wrap", alignItems: "center" }}>
          <span style={{ fontSize: 11.5, color: "#475569", fontWeight: 600 }}>Quick:</span>
          {QUICK.map(q => {
            const active = query === q;
            const m = dm(q);
            return (
              <button key={q} onClick={() => { setQuery(active ? "" : q); setPage(1); }} style={{
                padding: "4px 13px", background: active ? m.bg : "#162030",
                color: active ? m.accent : "#64748b",
                border: `1.5px solid ${active ? m.accent : "rgba(255,255,255,0.07)"}`,
                borderRadius: 20, cursor: "pointer", fontSize: 12, fontWeight: 700, transition: "all 0.14s",
              }}>{q}</button>
            );
          })}
          {(query || domain) && <button onClick={() => { setQuery(""); setDomain(""); setPage(1); }} style={{ marginLeft: "auto", padding: "4px 11px", background: "rgba(239,68,68,0.1)", border: "1px solid rgba(239,68,68,0.2)", borderRadius: 20, fontSize: 11.5, color: "#f87171", fontWeight: 600 }}>Clear All ✕</button>}
        </div>
      </div>

      <div style={{ fontSize: 12.5, color: "#475569", marginBottom: 12 }}>
        <strong style={{ color: "#94a3b8" }}>{results.length}</strong> result{results.length !== 1 ? "s" : ""}
        {query && <span> for "<strong style={{ color: "#34d399" }}>{query}</strong>"</span>}
      </div>

      {results.slice((page - 1) * itemsPerPage, page * itemsPerPage).map((r, i) => (
        <RequirementCard key={r.req_id} r={r} query={query} m={dm(r.domain)} i={i} />
      ))}

      {results.length > 0 && (
        <div style={{ padding: "14px 18px", background: "#162030", borderRadius: 8, border: "1px solid rgba(255,255,255,0.04)", fontSize: 11.5, color: "#475569", display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: 16 }}>
          <span>Showing {(page - 1) * itemsPerPage + 1} - {Math.min(page * itemsPerPage, results.length)} of {results.length}</span>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={{ ...inp, padding: "5px 10px" }}>Prev</button>
            <span>Page {page} of {Math.ceil(results.length / itemsPerPage) || 1}</span>
            <button onClick={() => setPage(p => Math.min(Math.ceil(results.length / itemsPerPage), p + 1))} disabled={page >= Math.ceil(results.length / itemsPerPage)} style={{ ...inp, padding: "5px 10px" }}>Next</button>
          </div>
        </div>
      )}

      {results.length === 0 && (
        <div style={{ textAlign: "center", padding: "60px 40px" }}>
          <div style={{ fontSize: 44, marginBottom: 10 }}>🔍</div>
          <div style={{ fontSize: 16, fontWeight: 700, color: "#64748b" }}>No requirements found</div>
          <button onClick={() => { setQuery(""); setDomain(""); setPage(1); }} style={{ marginTop: 18, padding: "10px 24px", background: "#10b981", color: "#fff", border: "none", borderRadius: 8, fontWeight: 700 }}>Clear Search</button>
        </div>
      )}
    </div>
  );
}
