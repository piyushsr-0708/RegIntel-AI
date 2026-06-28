import { useEffect, useRef, useState } from "react";
import cytoscape from "cytoscape";
import { useLocation } from "react-router-dom";
import { graphData as globalGraphData } from "../data/demo";
import { useAnalysisSession } from "../context/AnalysisSession";
import Breadcrumbs from "../components/Breadcrumbs";

const NM = {
  circular:    { bg: "#1d4ed8", border: "#60a5fa", glow: "rgba(96,165,250,0.55)",  shape: "round-rectangle", label: "RBI Circular",  emoji: "📜" },
  requirement: { bg: "#065f46", border: "#34d399", glow: "rgba(52,211,153,0.55)",  shape: "ellipse",          label: "Requirement",   emoji: "📋" },
  map:         { bg: "#7c2d12", border: "#fb923c", glow: "rgba(251,146,60,0.55)",  shape: "diamond",          label: "MAP",           emoji: "🎯" },
  department:  { bg: "#4c1d95", border: "#a78bfa", glow: "rgba(167,139,250,0.55)", shape: "hexagon",          label: "Department",    emoji: "🏛" },
};

export default function Graph() {
  const cyRef   = useRef(null);
  const contRef = useRef(null);
  const [sel, setSel] = useState(null);
  const { pathname } = useLocation();
  const isDocumentScoped = pathname.includes('/pipeline/analysis');
  const { session, hasSession } = useAnalysisSession();
  const [viewMode, setViewMode] = useState(isDocumentScoped && hasSession ? "active" : "global");
  
  const graphData = viewMode === "active" && hasSession ? session.analysis.scopedGraph : globalGraphData;

  const counts = {
    circular:    graphData.nodes.filter(n => n.data.type === "circular").length,
    requirement: graphData.nodes.filter(n => n.data.type === "requirement").length,
    map:         graphData.nodes.filter(n => n.data.type === "map").length,
  };

  useEffect(() => {
    cyRef.current = cytoscape({
      container: contRef.current,
      elements: [...graphData.nodes, ...graphData.edges],
      style: [
        { selector: "node", style: {
          label: "data(label)", "text-valign": "center", "text-halign": "center",
          "font-size": 10.5, "font-weight": 800, "text-wrap": "wrap", "text-max-width": 86,
          color: "#fff", "text-outline-color": "#0f1923", "text-outline-width": 1.5,
          "background-color": e => NM[e.data("type")]?.bg || "#1a2332",
          "border-color":     e => NM[e.data("type")]?.border || "#475569",
          "border-width": 2.5,
          shape: e => NM[e.data("type")]?.shape || "ellipse",
          width:  e => e.data("type") === "circular" ? 112 : e.data("type") === "requirement" ? 92 : 80,
          height: e => e.data("type") === "circular" ? 56 : 46,
          "transition-property": "border-width, border-color", "transition-duration": "0.2s"
        }},
        { selector: "node:selected", style: { "border-width": 6, "border-color": "#fcd34d", "box-shadow": "0 0 20px #fbbf24" }},
        { selector: "node:active",   style: { "overlay-opacity": 0 }},
        { selector: "edge", style: {
          label: "data(label)", "font-size": 9.5, "font-weight": 700,
          color: "#94a3b8", "text-outline-color": "#0f1923", "text-outline-width": 2,
          "curve-style": "bezier",
          "target-arrow-shape": "triangle",
          "line-color": "rgba(71,85,105,0.5)", "target-arrow-color": "rgba(71,85,105,0.5)",
          width: 1.5,
        }},
        { selector: "edge[label='generates']", style: { "line-color": "rgba(251,191,36,0.65)", "target-arrow-color": "rgba(251,191,36,0.65)", width: 2 }},
        { selector: "edge[label='defines']",   style: { "line-color": "rgba(96,165,250,0.65)", "target-arrow-color": "rgba(96,165,250,0.65)", width: 2 }},
        { selector: ".faded", style: { opacity: 0.15, "text-opacity": 0 } },
      ],
      layout: { name: "cose", idealEdgeLength: 160, nodeOverlap: 30, animate: true, animationDuration: 700, randomize: false, padding: 60, gravity: 0.15 },
      userZoomingEnabled: true, userPanningEnabled: true, minZoom: 0.2, maxZoom: 4, wheelSensitivity: 0.2,
    });

    cyRef.current.ready(() => {
      setTimeout(() => cyRef.current?.fit(undefined, 40), 800);
    });

    cyRef.current.on("tap", "node", evt => {
      const n = evt.target;
      const edges = n.connectedEdges();
      const connected = n.closedNeighborhood();
      
      cyRef.current.elements().removeClass("faded");
      cyRef.current.elements().not(connected).addClass("faded");

      setSel({ id: n.id(), label: n.data("label"), type: n.data("type"), connections: edges.connectedNodes().not(n).length, edges: edges.map(e => ({ label: e.data("label"), source: e.data("source"), target: e.data("target") })) });
    });
    cyRef.current.on("tap", evt => { 
      if (evt.target === cyRef.current) {
        cyRef.current.elements().removeClass("faded");
        setSel(null); 
      }
    });
    return () => cyRef.current?.destroy();
  }, []);

  return (
    <div>
      <Breadcrumbs />
      <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#a78bfa,#7c3aed)", boxShadow: "0 0 10px rgba(139,92,246,0.4)" }} />
            <h1 className="page-title">{viewMode === "active" ? "Document Knowledge Graph" : "Knowledge Graph"}</h1>
          </div>
          <p className="page-subtitle" style={{ paddingLeft: 14 }}>Regulatory relationship network · RBI Circulars → Requirements → MAPs</p>
        </div>
        {hasSession && (
          <div style={{ display: "flex", gap: 8, background: "rgba(10,18,32,0.6)", padding: 4, borderRadius: 10, border: "1px solid rgba(255,255,255,0.05)" }}>
            <button 
              onClick={() => setViewMode("global")} 
              style={{ padding: "8px 16px", borderRadius: 7, border: "none", fontSize: 12, fontWeight: 700, cursor: "pointer", transition: "all 0.2s",
                background: viewMode === "global" ? "rgba(167,139,250,0.15)" : "transparent",
                color: viewMode === "global" ? "#c4b5fd" : "#64748b"
              }}>
              Global Graph
            </button>
            <button 
              onClick={() => setViewMode("active")} 
              style={{ padding: "8px 16px", borderRadius: 7, border: "none", fontSize: 12, fontWeight: 700, cursor: "pointer", transition: "all 0.2s",
                background: viewMode === "active" ? "rgba(167,139,250,0.15)" : "transparent",
                color: viewMode === "active" ? "#c4b5fd" : "#64748b"
              }}>
              Active Session
            </button>
          </div>
        )}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 288px", gap: 16, alignItems: "start" }}>
        {/* Canvas */}
        <div style={{ borderRadius: 12, overflow: "hidden", position: "relative", background: "#0a1220", border: "1px solid rgba(255,255,255,0.06)", boxShadow: "0 8px 32px rgba(0,0,0,0.4)" }}>
          {/* Legend */}
          <div style={{ position: "absolute", top: 12, left: 12, zIndex: 10, background: "rgba(10,18,32,0.92)", borderRadius: 9, padding: "11px 14px", border: "1px solid rgba(255,255,255,0.07)", backdropFilter: "blur(6px)" }}>
            <div style={{ fontSize: 9.5, color: "#334155", fontWeight: 700, letterSpacing: 1, marginBottom: 9, textTransform: "uppercase" }}>Legend</div>
            {Object.entries(NM).filter(([k]) => isDocumentScoped || k !== "department").map(([type, m]) => (
              <div key={type} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7 }}>
                <div style={{ width: 20, height: 13, borderRadius: type === "requirement" ? "50%" : type === "map" ? 2 : 3, background: m.bg, border: `1.5px solid ${m.border}`, flexShrink: 0 }} />
                <div>
                  <div style={{ fontSize: 11, fontWeight: 700, color: "#e2e8f0" }}>{m.label}</div>
                </div>
              </div>
            ))}
          </div>
          {/* Controls */}
          <div style={{ position: "absolute", top: 12, right: 12, zIndex: 10, display: "flex", gap: 5 }}>
            {[["⊞", "Fit", () => cyRef.current?.fit(undefined, 40)], ["⊙", "Reset", () => cyRef.current?.zoom({ level: 1 })]].map(([icon, title, fn]) => (
              <button key={icon} title={title} onClick={fn} style={{ width: 30, height: 30, borderRadius: 7, background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.1)", color: "#94a3b8", fontSize: 14, display: "flex", alignItems: "center", justifyContent: "center", transition: "all 0.14s" }}
                onMouseEnter={e => e.currentTarget.style.background = "rgba(255,255,255,0.12)"}
                onMouseLeave={e => e.currentTarget.style.background = "rgba(255,255,255,0.06)"}>{icon}</button>
            ))}
          </div>
          {/* Edge legend */}
          <div style={{ position: "absolute", bottom: 12, left: 12, zIndex: 10, display: "flex", gap: 12, background: "rgba(10,18,32,0.88)", borderRadius: 7, padding: "7px 11px", border: "1px solid rgba(255,255,255,0.05)" }}>
            {[["rgba(96,165,250,0.8)","defines"],["rgba(251,191,36,0.8)","generates"],["rgba(71,85,105,0.6)","related"]].map(([c, l]) => (
              <div key={l} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10 }}>
                <div style={{ width: 14, height: 2, background: c, borderRadius: 1 }} />
                <span style={{ color: "#475569", fontWeight: 600 }}>{l}</span>
              </div>
            ))}
          </div>
          <div style={{ position: "absolute", bottom: 12, right: 12, zIndex: 10, fontSize: 9.5, color: "#334155" }}>Scroll · Drag · Click node</div>
          <div ref={contRef} style={{ width: "100%", height: 548 }} />
        </div>

        {/* Panel */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <div className="card" style={{ padding: 18 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", marginBottom: 14 }}>Graph Statistics</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 9 }}>
              {[
                ["Circulars",     counts.circular,    NM.circular.border],
                ["Requirements",  counts.requirement, NM.requirement.border],
                ["MAPs",          counts.map,         NM.map.border],
                ["Relationships", graphData.edges.length, "#64748b"],
              ].map(([label, value, color]) => (
                <div key={label} style={{ textAlign: "center", padding: "10px 8px", background: "#162030", borderRadius: 8, border: `1px solid ${color}20` }}>
                  <div style={{ fontSize: 22, fontWeight: 900, color, lineHeight: 1 }}>{value}</div>
                  <div style={{ fontSize: 10, color: "#475569", marginTop: 3, fontWeight: 600 }}>{label}</div>
                </div>
              ))}
            </div>
          </div>

          {sel ? (
            <div className="card" style={{ padding: 18 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <span style={{ fontSize: 16 }}>{NM[sel.type]?.emoji}</span>
                <div>
                  <div style={{ fontSize: 9.5, color: "#475569", fontWeight: 700, letterSpacing: 0.5 }}>SELECTED</div>
                  <div style={{ fontSize: 11.5, fontWeight: 700, color: NM[sel.type]?.border }}>{NM[sel.type]?.label}</div>
                </div>
              </div>
              <div style={{ marginBottom: 10 }}>
                <div style={{ fontSize: 9.5, color: "#475569", fontWeight: 700, marginBottom: 3 }}>NODE ID</div>
                <span style={{ fontFamily: "monospace", fontSize: 11.5, fontWeight: 700, color: "#34d399", background: "rgba(52,211,153,0.1)", padding: "3px 8px", borderRadius: 5 }}>{sel.id}</span>
              </div>
              <div style={{ marginBottom: 12 }}>
                <div style={{ fontSize: 9.5, color: "#475569", fontWeight: 700, marginBottom: 4 }}>LABEL</div>
                <div style={{ fontSize: 12, color: "#94a3b8", lineHeight: 1.6, background: "#162030", padding: "8px 10px", borderRadius: 7 }}>{sel.label}</div>
              </div>
              <div style={{ marginBottom: 14 }}>
                <div style={{ fontSize: 9.5, color: "#475569", fontWeight: 700, marginBottom: 7 }}>CONNECTIONS ({sel.connections})</div>
                <div style={{ maxHeight: 150, overflowY: "auto", display: "flex", flexDirection: "column", gap: 4 }}>
                  {sel.edges.map((e, i) => (
                    <div key={i} style={{ display: "flex", alignItems: "center", gap: 5, padding: "4px 8px", background: "#162030", borderRadius: 5, fontSize: 10.5 }}>
                      <div style={{ width: 16, height: 1.5, background: e.label === "generates" ? "#fbbf24" : e.label === "defines" ? "#60a5fa" : "#475569", flexShrink: 0 }} />
                      <span style={{ color: "#64748b", fontWeight: 600 }}>{e.label}</span>
                      <span style={{ color: "#334155" }}>→</span>
                      <span style={{ color: "#94a3b8", fontWeight: 600 }}>{e.source === sel.id ? e.target : e.source}</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* AI Explainability */}
              <div style={{ padding: "12px 14px", background: "rgba(96,165,250,0.06)", border: "1px solid rgba(96,165,250,0.15)", borderRadius: 8 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 10, color: "#60a5fa", fontWeight: 800, marginBottom: 6, letterSpacing: 0.5 }}>
                  <svg width="12" height="12" fill="none" stroke="currentColor" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M12 2v20m-7-7h14m-10-6h6"/></svg>
                  AI GRAPH EXPLANATION
                </div>
                <div style={{ fontSize: 11.5, color: "#e2e8f0", lineHeight: 1.6 }}>
                  This <strong>{sel.type}</strong> node represents an extracted compliance entity. RegIntel AI deterministically linked it to <strong>{sel.connections}</strong> other entities based on semantic references discovered during the initial text processing pipeline. Highlighting this cluster isolates the localized regulatory impact graph.
                </div>
              </div>
            </div>
          ) : (
            <div className="card" style={{ padding: 18 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", marginBottom: 12 }}>How to Use</div>
              {[["🖱","Click node to inspect"], ["🔍","Scroll to zoom"], ["✋","Drag to pan"], ["⊞","Fit button resets view"]].map(([icon, text]) => (
                <div key={text} style={{ display: "flex", gap: 9, marginBottom: 8, padding: "7px 10px", background: "#162030", borderRadius: 7 }}>
                  <span style={{ fontSize: 13, flexShrink: 0 }}>{icon}</span>
                  <span style={{ fontSize: 12, color: "#64748b" }}>{text}</span>
                </div>
              ))}
              <div style={{ marginTop: 10, padding: "9px 12px", background: "rgba(16,185,129,0.07)", borderRadius: 7, border: "1px solid rgba(16,185,129,0.15)", fontSize: 11.5, color: "#34d399", lineHeight: 1.65 }}>
                Blue = <strong>defines</strong> (Circular→Req)<br/>
                Amber = <strong>generates</strong> (Req→MAP)
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
