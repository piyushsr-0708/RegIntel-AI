import { useState, useMemo, memo, useContext } from "react";
import { DemoContext } from "../App";
import { useNavigate, useLocation } from "react-router-dom";
import { mapsOutput as globalMapsOutput } from "../data/demo";
import { PriorityBadge, StatusBadge, ImpactScore } from "../components/Badges";
import { useAnalysisSession } from "../context/AnalysisSession";
import Breadcrumbs from "../components/Breadcrumbs";

const MapRow = memo(({ m, navigate, isNew }) => (
  <tr onClick={() => navigate(`/maps/${m.map_id}`)} style={isNew ? { background: "rgba(139,92,246,0.1)", borderLeft: "2px solid #8b5cf6" } : {}}>
    <td>
      <span style={{ fontFamily: "monospace", fontSize: 11.5, fontWeight: 700, color: "#34d399", background: "rgba(52,211,153,0.1)", padding: "3px 7px", borderRadius: 5 }}>{m.map_id}</span>
      {isNew && <span style={{ marginLeft: 6, fontSize: 9, background: "#8b5cf6", color: "#fff", padding: "2px 5px", borderRadius: 4, fontWeight: 800 }}>NEW</span>}
    </td>
    <td style={{ maxWidth: 290, color: "#d1d5db", fontWeight: 500, lineHeight: 1.4 }}>{m.title}</td>
    <td><span style={{ fontSize: 11.5, color: "#94a3b8", background: "#162030", padding: "3px 9px", borderRadius: 6, border: "1px solid rgba(255,255,255,0.06)" }}>{m.department}</span></td>
    <td><PriorityBadge priority={m.priority} /></td>
    <td><ImpactScore score={m.impact_score} /></td>
    <td style={{ fontSize: 12, color: m.deadline < new Date().toISOString().split("T")[0] ? "#f87171" : "#64748b", fontWeight: m.deadline < new Date().toISOString().split("T")[0] ? 700 : 400 }}>{m.deadline}</td>
    <td><StatusBadge status={m.status} /></td>
    <td style={{ color: "#334155", fontSize: 18, paddingRight: 8 }}>›</td>
  </tr>
));

const PRIORITIES  = ["Critical","High","Medium","Low"];
const STATUSES    = ["Pending","In Progress","Completed","Overdue"];
const PORDER      = { Critical:0, High:1, Medium:2, Low:3 };

const inp = {
  background: "#162030", border: "1.5px solid rgba(255,255,255,0.07)", borderRadius: 7,
  padding: "9px 12px", fontSize: 12.5, color: "#e2e8f0",
  transition: "border-color 0.15s, box-shadow 0.15s",
};

export default function Maps() {
  const navigate = useNavigate();
  const { pathname } = useLocation();
  const isDocumentScoped = pathname.includes('/pipeline/analysis');
  const { session, hasSession } = useAnalysisSession();
  
  const mapsOutput = isDocumentScoped && hasSession ? session.analysis.maps : globalMapsOutput;
  const DEPARTMENTS = useMemo(() => [...new Set(mapsOutput.map((m) => m.department))].sort(), [mapsOutput]);

  const [search, setSearch]   = useState("");
  const [dept, setDept]       = useState("");
  const [priority, setPri]    = useState("");
  const [status, setStatus]   = useState("");
  const [sortBy, setSortBy]   = useState("impact_score");
  const [sortDir, setSortDir] = useState("desc");
  const [page, setPage]       = useState(1);
  const itemsPerPage = 50;
  const { isDemo } = useContext(DemoContext);

  const filtered = useMemo(() => {
    const q = search.toLowerCase();
    let data = mapsOutput.filter((m) =>
      (!q || m.map_id.toLowerCase().includes(q) || m.title.toLowerCase().includes(q) || m.department.toLowerCase().includes(q)) &&
      (!dept     || m.department === dept) &&
      (!priority || m.priority   === priority) &&
      (!status   || m.status     === status)
    );
    return [...data].sort((a, b) => {
      const av = sortBy === "priority" ? PORDER[a.priority] : a[sortBy];
      const bv = sortBy === "priority" ? PORDER[b.priority] : b[sortBy];
      if (typeof av === "string") return sortDir === "asc" ? av.localeCompare(bv) : bv.localeCompare(av);
      return sortDir === "asc" ? av - bv : bv - av;
    });
  }, [mapsOutput, search, dept, priority, status, sortBy, sortDir]);

  const toggleSort = (col) => {
    if (sortBy === col) setSortDir(d => d === "asc" ? "desc" : "asc");
    else { setSortBy(col); setSortDir("desc"); }
  };

  const SortIcon = ({ col }) => (
    <span style={{ marginLeft: 3, opacity: sortBy === col ? 1 : 0.25, fontSize: 10 }}>
      {sortBy !== col ? "↕" : sortDir === "asc" ? "↑" : "↓"}
    </span>
  );

  return (
    <div>
      <Breadcrumbs />
      <div className="page-header" style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#a78bfa,#7c3aed)", boxShadow: "0 0 10px rgba(139,92,246,0.4)" }} />
            <h1 className="page-title">{isDocumentScoped ? "Document MAPs" : "MAP Management"}</h1>
          </div>
          <p className="page-subtitle" style={{ paddingLeft: 14 }}>
            Showing <strong style={{ color: "#f1f5f9" }}>{filtered.length}</strong> of {mapsOutput.length} Mitigation Action Plans
          </p>
        </div>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
          {isDocumentScoped && (
            <button onClick={() => window.location.href = "/maps"} style={{ padding: "8px 18px", borderRadius: 8, background: "rgba(167,139,250,0.12)", border: "1px solid rgba(167,139,250,0.3)", color: "#c4b5fd", fontSize: 12, fontWeight: 700, cursor: "pointer", height: "fit-content", marginRight: 16 }}>
              Open Full Repository
            </button>
          )}
          {[["Critical", mapsOutput.filter(m=>m.priority==="Critical").length, "#f87171","rgba(239,68,68,0.12)"],
            ["Overdue",  mapsOutput.filter(m=>m.status==="Overdue").length,    "#fbbf24","rgba(251,191,36,0.1)"]].map(([lbl,val,c,bg]) => (
            <div key={lbl} style={{ background: bg, border: `1px solid ${c}25`, borderRadius: 9, padding: "9px 16px", textAlign: "center" }}>
              <div style={{ fontSize: 22, fontWeight: 900, color: c, lineHeight: 1 }}>{val}</div>
              <div style={{ fontSize: 10.5, color: "#64748b", marginTop: 2, fontWeight: 600 }}>{lbl}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Filters */}
      <div className="card" style={{ padding: "14px 18px", marginBottom: 16, display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center" }}>
        <div style={{ position: "relative", flex: 1, minWidth: 200 }}>
          <svg style={{ position: "absolute", left: 10, top: "50%", transform: "translateY(-50%)", opacity: 0.35 }} width="13" height="13" fill="none" stroke="#94a3b8" strokeWidth="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
          <input placeholder="Search MAP ID, title, department…" value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
            style={{ ...inp, width: "100%", paddingLeft: 30 }}
            onFocus={e => { e.target.style.borderColor = "#10b981"; e.target.style.boxShadow = "0 0 0 3px rgba(16,185,129,0.12)"; }}
            onBlur={e  => { e.target.style.borderColor = "rgba(255,255,255,0.07)"; e.target.style.boxShadow = "none"; }}
          />
        </div>
        {[
          { val: dept,     set: setDept,   opts: DEPARTMENTS, ph: "All Departments" },
          { val: priority, set: setPri,    opts: PRIORITIES,  ph: "All Priorities" },
          { val: status,   set: setStatus, opts: STATUSES,    ph: "All Statuses" },
        ].map((s, i) => (
          <select key={i} value={s.val} onChange={e => s.set(e.target.value)} style={{ ...inp, minWidth: 140 }}
            onFocus={e => e.target.style.borderColor = "#10b981"}
            onBlur={e  => e.target.style.borderColor = "rgba(255,255,255,0.07)"}>
            <option value="">{s.ph}</option>
            {s.opts.map(o => <option key={o}>{o}</option>)}
          </select>
        ))}
        <div style={{ width: 1, height: 26, background: "rgba(255,255,255,0.06)" }} />
        <select value={sortBy} onChange={e => { setSortBy(e.target.value); setPage(1); }} style={{ ...inp, minWidth: 148 }}>
          <option value="impact_score">↓ Impact Score</option>
          <option value="priority">↓ Priority</option>
          <option value="department">↓ Department</option>
          <option value="deadline">↓ Deadline</option>
        </select>
        {(search || dept || priority || status) && (
          <button onClick={() => { setSearch(""); setDept(""); setPri(""); setStatus(""); setPage(1); }}
            style={{ ...inp, border: "1.5px solid rgba(239,68,68,0.25)", color: "#f87171", padding: "9px 14px", fontSize: 12 }}>
            ✕ Clear
          </button>
        )}
      </div>

      {/* Table */}
      <div className="card" style={{ overflow: "hidden" }}>
        <table className="data-table">
          <thead>
            <tr>
              {[["MAP ID","map_id"],["Task Title","title"],["Department","department"],["Priority","priority"],["Impact","impact_score"],["Deadline","deadline"],["Status","status"],["",""]].map(([lbl,col]) => (
                <th key={col} onClick={() => col && toggleSort(col)}>
                  {lbl}{col && lbl && <SortIcon col={col} />}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.slice((page - 1) * itemsPerPage, page * itemsPerPage).map((m, i) => (
              <MapRow key={m.map_id} m={m} navigate={navigate} isNew={isDemo && i < 2 && page === 1 && !search} />
            ))}
          </tbody>
        </table>
        {filtered.length === 0 && (
          <div style={{ padding: "52px 40px", textAlign: "center" }}>
            <div style={{ fontSize: 34, marginBottom: 10 }}>🔍</div>
            <div style={{ fontSize: 15, fontWeight: 700, color: "#94a3b8" }}>No MAPs found</div>
            <div style={{ fontSize: 12.5, color: "#475569", marginTop: 4 }}>Try adjusting your filters</div>
          </div>
        )}
        <div style={{ padding: "11px 18px", background: "#162030", borderTop: "1px solid rgba(255,255,255,0.04)", fontSize: 11.5, color: "#475569", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <span>{filtered.length} records</span>
          <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
            <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} style={{ ...inp, padding: "5px 10px" }}>Prev</button>
            <span>Page {page} of {Math.ceil(filtered.length / itemsPerPage) || 1}</span>
            <button onClick={() => setPage(p => Math.min(Math.ceil(filtered.length / itemsPerPage), p + 1))} disabled={page >= Math.ceil(filtered.length / itemsPerPage)} style={{ ...inp, padding: "5px 10px" }}>Next</button>
          </div>
        </div>
      </div>
    </div>
  );
}
