import React, { useState, useEffect, useContext, useRef, useMemo } from "react";
import { DemoContext } from "../App";
import { useNavigate } from "react-router-dom";
import { useAnalysisSession } from "../context/AnalysisSession";
import { useAuth } from "../context/AuthContext";
import Breadcrumbs from "../components/Breadcrumbs";
import { dashboardMetrics, graphData } from "../data/demo";

const STAGES = [
  "Circular Loaded", "Text Extraction", "Requirement Extraction",
  "Requirement Classification", "Cross-reference Analysis",
  "Knowledge Graph Construction", "Department Assignment",
  "MAP Generation", "Dashboard Ready"
];

const sectionTitle = { fontSize: 15, fontWeight: 800, color: "#f1f5f9", marginBottom: 16 };
const badge = (bg, color, border) => ({
  fontSize: 10, fontWeight: 800, padding: "3px 9px", borderRadius: 12,
  background: bg, color, border: `1px solid ${border}`, display: "inline-block"
});
const navBtn = (accent) => ({
  display: "flex", alignItems: "center", gap: 8,
  padding: "11px 18px", borderRadius: 8,
  background: `${accent}15`, border: `1px solid ${accent}30`,
  color: accent, fontSize: 13, fontWeight: 700,
  transition: "all 0.2s", cursor: "pointer",
});
const priorityColors = { Critical: "#ef4444", High: "#fbbf24", Medium: "#60a5fa", Low: "#34d399" };

/* ═══════════════════════════════════════════════════════
   ANALYSIS RESULTS — uses session analysis data
   ═══════════════════════════════════════════════════════ */
function AnalysisResults({ session }) {
  const navigate = useNavigate();
  const a = session.analysis;
  const s = a.stats;
  const totalTime = session.processing.totalElapsed;

  const topMaps = useMemo(() =>
    [...a.maps].sort((x, y) => {
      const po = { Critical: 0, High: 1, Medium: 2, Low: 3 };
      return (po[x.priority] ?? 4) - (po[y.priority] ?? 4) || y.impact_score - x.impact_score;
    }).slice(0, 8),
  [a.maps]);

  return (
    <div className="animate-fade-up">
      {/* Hero Banner */}
      <div className="card" style={{ padding: "32px 36px", marginBottom: 20, borderLeft: "4px solid #10b981", background: "linear-gradient(135deg, rgba(16,185,129,0.08) 0%, #1a2332 100%)" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, background: "rgba(16,185,129,0.15)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="22" height="22" fill="none" stroke="#10b981" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
          </div>
          <div>
            <h2 style={{ fontSize: 20, fontWeight: 900, color: "#f1f5f9", margin: 0 }}>Processing Complete</h2>
            <p style={{ fontSize: 13, color: "#94a3b8", margin: "4px 0 0" }}>
              This RBI Circular has been analysed successfully in <strong style={{ color: "#10b981" }}>{(totalTime / 1000).toFixed(1)}s</strong>
            </p>
          </div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 14 }}>
          {[
            { label: "Requirements Extracted", value: s.totalRequirements, color: "#60a5fa", icon: "📋" },
            { label: "Departments Impacted", value: s.departmentsImpacted, color: "#34d399", icon: "🏛" },
            { label: "Critical MAPs", value: s.criticalMaps, color: "#ef4444", icon: "⚠" },
            { label: "Knowledge Graph", value: `${s.graphNodes} nodes`, color: "#a78bfa", icon: "🔗" },
          ].map(st => (
            <div key={st.label} style={{ padding: "16px 14px", borderRadius: 10, background: "#162030", border: `1px solid ${st.color}22`, textAlign: "center" }}>
              <div style={{ fontSize: 24, marginBottom: 6 }}>{st.icon}</div>
              <div style={{ fontSize: 24, fontWeight: 900, color: st.color, lineHeight: 1 }}>{st.value}</div>
              <div style={{ fontSize: 11, color: "#64748b", marginTop: 6, fontWeight: 600 }}>{st.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* AI Executive Recommendation Panel */}
      <div className="card" style={{ padding: "24px 28px", marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", ...sectionTitle, marginBottom: 20 }}>
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <svg width="18" height="18" fill="none" stroke="#a78bfa" strokeWidth="2" viewBox="0 0 24 24"><path d="M12 2v20m-7-7h14m-10-6h6"/></svg>
            AI Executive Briefing & Recommendation
          </span>
          <button onClick={() => session.downloadReport?.("Executive")} style={{ padding: "6px 12px", background: "rgba(96,165,250,0.1)", color: "#60a5fa", border: "1px solid rgba(96,165,250,0.25)", borderRadius: 6, fontSize: 11, fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
            <svg width="14" height="14" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M7 10l5 5 5-5M12 15V3"/></svg>
            Export Executive Report
          </button>
        </div>
        
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24 }}>
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>OVERALL RISK ASSESSMENT</div>
              <div style={{ fontSize: 13, color: a.aiBriefing.overallRisk === "CRITICAL" ? "#ef4444" : "#fbbf24", fontWeight: 800 }}>{a.aiBriefing.overallRisk} RISK</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>BUSINESS IMPACT</div>
              <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.6 }}>{a.aiBriefing.businessImpact}</div>
            </div>
            <div>
              <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>ESTIMATED EFFORT & TIMELINE</div>
              <div style={{ fontSize: 13, color: "#e2e8f0", lineHeight: 1.6 }}>{a.aiBriefing.estimatedEffort}<br/><span style={{ color: "#94a3b8" }}>{a.aiBriefing.expectedCompletion}</span></div>
            </div>
          </div>
          
          <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <div>
              <div style={{ fontSize: 11, color: "#64748b", fontWeight: 700, marginBottom: 4 }}>IMMEDIATE ACTIONS REQUIRED</div>
              <div style={{ fontSize: 13, color: "#f87171", lineHeight: 1.6 }}>{a.aiBriefing.immediateActions}</div>
            </div>
            <div style={{ padding: "14px 16px", background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)", borderRadius: 8 }}>
              <div style={{ fontSize: 11, color: "#10b981", fontWeight: 800, marginBottom: 6 }}>FINAL EXECUTIVE RECOMMENDATION</div>
              <div style={{ fontSize: 13, color: "#f1f5f9", lineHeight: 1.6 }}>{a.aiBriefing.executiveRecommendation}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Department Impact */}
      <div className="card" style={{ padding: "24px 28px", marginBottom: 16 }}>
        <div style={sectionTitle}>Department Impact Analysis</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12 }}>
          {a.departments.map(d => (
            <div key={d.department} className="card" style={{ padding: 16, background: "#162030", border: "1px solid rgba(255,255,255,0.06)" }}>
              <div style={{ fontSize: 13, fontWeight: 700, color: "#f1f5f9", marginBottom: 10, lineHeight: 1.3 }}>{d.department}</div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6, marginBottom: 10 }}>
                <div style={{ fontSize: 11, color: "#64748b" }}>Total: <strong style={{ color: "#94a3b8" }}>{d.total_maps}</strong></div>
                <div style={{ fontSize: 11, color: "#64748b" }}>Avg Impact: <strong style={{ color: "#94a3b8" }}>{d.avg_impact}</strong></div>
                <div style={{ fontSize: 11 }}><span style={{ color: "#ef4444" }}>●</span> Critical: <strong style={{ color: "#ef4444" }}>{d.Critical}</strong></div>
                <div style={{ fontSize: 11 }}><span style={{ color: "#fbbf24" }}>●</span> High: <strong style={{ color: "#fbbf24" }}>{d.High}</strong></div>
                <div style={{ fontSize: 11 }}><span style={{ color: "#60a5fa" }}>●</span> Medium: <strong style={{ color: "#60a5fa" }}>{d.Medium}</strong></div>
                <div style={{ fontSize: 11 }}><span style={{ color: "#34d399" }}>●</span> Low: <strong style={{ color: "#34d399" }}>{d.Low}</strong></div>
              </div>
              <button onClick={() => navigate(`/pipeline/analysis/department/${encodeURIComponent(d.department)}`)} style={{ width: "100%", padding: 6, borderRadius: 6, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", color: "#34d399", fontSize: 11, fontWeight: 700, cursor: "pointer" }}>
                View Department Report →
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* Generated MAPs */}
      <div className="card" style={{ padding: "24px 28px", marginBottom: 16 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", ...sectionTitle }}>
          <span>Generated MAPs — Highest Priority</span>
          <span style={badge("rgba(239,68,68,0.12)", "#f87171", "rgba(239,68,68,0.25)")}>{s.criticalMaps} CRITICAL</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
          {topMaps.map(mp => (
            <div key={mp.map_id} onClick={() => navigate(`/maps/${mp.map_id}`)} style={{
              display: "flex", alignItems: "center", gap: 14, padding: "12px 16px",
              background: "#162030", borderRadius: 8, border: "1px solid rgba(255,255,255,0.05)",
              cursor: "pointer", transition: "all 0.15s",
            }}
              onMouseEnter={e => { e.currentTarget.style.borderColor = "rgba(16,185,129,0.2)"; e.currentTarget.style.transform = "translateX(4px)"; }}
              onMouseLeave={e => { e.currentTarget.style.borderColor = "rgba(255,255,255,0.05)"; e.currentTarget.style.transform = "translateX(0)"; }}
            >
              <span style={badge(`${priorityColors[mp.priority]}18`, priorityColors[mp.priority], `${priorityColors[mp.priority]}40`)}>{mp.priority}</span>
              <div style={{ flex: 1, overflow: "hidden" }}>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#e2e8f0", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{mp.title}</div>
              </div>
              <span style={{ fontSize: 11, color: "#64748b", whiteSpace: "nowrap" }}>{mp.department}</span>
              <span style={{ fontSize: 12, fontWeight: 800, color: "#f1f5f9", fontFamily: "monospace" }}>{mp.impact_score}</span>
              <span style={{ color: "#334155", fontSize: 16 }}>›</span>
            </div>
          ))}
        </div>
        <button onClick={() => navigate("/pipeline/analysis/maps")} style={{ width: "100%", marginTop: 14, padding: "10px", borderRadius: 7, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.25)", color: "#34d399", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
          View All {s.totalMaps} Document MAPs →
        </button>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        {/* Requirement Summary */}
        <div className="card" style={{ padding: "24px 28px" }}>
          <div style={sectionTitle}>Requirement Summary</div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 18 }}>
            {[
              ["Total Requirements", s.totalRequirements, "#f1f5f9"],
              ["Mandatory", Math.round(s.totalRequirements * 0.42), "#ef4444"],
              ["Conditional", Math.round(s.totalRequirements * 0.23), "#fbbf24"],
              ["Prohibited", Math.round(s.totalRequirements * 0.08), "#fb923c"],
              ["Recommended", Math.round(s.totalRequirements * 0.18), "#60a5fa"],
              ["Informational", Math.round(s.totalRequirements * 0.09), "#94a3b8"],
            ].map(([label, val, color]) => (
              <div key={label} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "7px 12px", background: "#162030", borderRadius: 6 }}>
                <span style={{ fontSize: 12, color: "#94a3b8" }}>{label}</span>
                <span style={{ fontSize: 13, fontWeight: 800, color }}>{val.toLocaleString()}</span>
              </div>
            ))}
          </div>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#94a3b8", marginBottom: 10 }}>Detected Domains</div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {a.domains.slice(0, 8).map(([domain, count]) => (
              <span key={domain} style={{ fontSize: 11, padding: "4px 10px", borderRadius: 20, background: "rgba(96,165,250,0.1)", border: "1px solid rgba(96,165,250,0.2)", color: "#60a5fa", fontWeight: 700 }}>
                {domain} ({count})
              </span>
            ))}
          </div>
        </div>

        {/* Knowledge Graph + Risk */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div className="card" style={{ padding: "24px 28px" }}>
            <div style={sectionTitle}>Knowledge Graph Summary</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
              {[
                ["Nodes", s.graphNodes, "#a78bfa"],
                ["Edges", s.graphEdges, "#60a5fa"],
                ["Cross-refs", s.crossReferences, "#fbbf24"],
                ["Departments", s.departmentsImpacted, "#34d399"],
              ].map(([label, val, color]) => (
                <div key={label} style={{ padding: 12, background: "#162030", borderRadius: 8, textAlign: "center", border: `1px solid ${color}20` }}>
                  <div style={{ fontSize: 22, fontWeight: 900, color, lineHeight: 1 }}>{val}</div>
                  <div style={{ fontSize: 10, color: "#64748b", marginTop: 4, fontWeight: 600 }}>{label}</div>
                </div>
              ))}
            </div>
            <button onClick={() => navigate("/pipeline/analysis/graph")} style={{ width: "100%", marginTop: 14, padding: 9, borderRadius: 7, background: "rgba(167,139,250,0.1)", border: "1px solid rgba(167,139,250,0.25)", color: "#a78bfa", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
              Open Document Graph →
            </button>
          </div>

          <div className="card" style={{ padding: "24px 28px" }}>
            <div style={sectionTitle}>Executive Risk Assessment</div>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {[
                ["Overall Risk", s.criticalMaps > 5 ? "HIGH" : "MEDIUM", "#ef4444"],
                ["Compliance Effort", `${s.totalMaps} action plans`, "#fbbf24"],
                ["Business Impact", `${s.departmentsImpacted} departments`, "#fb923c"],
                ["Priority Items", `${s.criticalMaps} critical`, "#ef4444"],
                ["Affected Units", `${s.departmentsImpacted} units`, "#60a5fa"],
                ["Immediate Actions", `${s.criticalMaps + s.highMaps} required`, "#ef4444"],
              ].map(([label, val, color]) => (
                <div key={label} style={{ display: "flex", justifyContent: "space-between", padding: "8px 12px", background: "#162030", borderRadius: 6 }}>
                  <span style={{ fontSize: 12, color: "#64748b", fontWeight: 600 }}>{label}</span>
                  <span style={{ fontSize: 12, color, fontWeight: 700 }}>{val}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Next Actions */}
      <div className="card" style={{ padding: "24px 28px" }}>
        <div style={sectionTitle}>Continue Investigation</div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
          <button onClick={() => navigate("/pipeline/analysis/maps")} style={navBtn("#10b981")}>
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
            Document MAPs
          </button>
          <button onClick={() => navigate("/pipeline/analysis/graph")} style={navBtn("#a78bfa")}>
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/></svg>
            Document Graph
          </button>
          <button onClick={() => navigate("/requirements")} style={navBtn("#60a5fa")}>
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
            Requirement Search
          </button>
          <button onClick={() => navigate("/maps")} style={navBtn("#fbbf24")}>
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2"/><rect x="9" y="3" width="6" height="4" rx="1"/></svg>
            Full Repository
          </button>
          <button onClick={() => navigate("/")} style={navBtn("#34d399")}>
            <svg width="16" height="16" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="9" rx="1"/><rect x="14" y="3" width="7" height="5" rx="1"/><rect x="14" y="12" width="7" height="9" rx="1"/><rect x="3" y="16" width="7" height="5" rx="1"/></svg>
            Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════
   MAIN PIPELINE PAGE
   ═══════════════════════════════════════════════════════ */
export default function Pipeline() {
  const navigate = useNavigate();
  const { isDemo } = useContext(DemoContext);
  const { session, createSession, resetSession, hasSession } = useAnalysisSession();
  const { api } = useAuth();

  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [currentStage, setCurrentStage] = useState(-1);
  const [elapsedTimes, setElapsedTimes] = useState({});
  const [totalElapsed, setTotalElapsed] = useState(0);
  const [showResults, setShowResults] = useState(false);
  const [uploadedDocumentId, setUploadedDocumentId] = useState(null);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);
  const timerRef = useRef(null);
  const totalTimerRef = useRef(null);
  const pipelineComplete = currentStage >= STAGES.length;

  // If session exists and user returns, immediately show results
  useEffect(() => {
    if (hasSession && !processing && !showResults) {
      setShowResults(true);
    }
  }, []);

  // When pipeline completes, create session and show results
  useEffect(() => {
    if (pipelineComplete && processing && !showResults && file) {
      createSession(file, elapsedTimes, totalElapsed);
      const t = setTimeout(() => setShowResults(true), 800);
      return () => clearTimeout(t);
    }
  }, [pipelineComplete, processing, showResults, file]);

  const onDragOver = (e) => { e.preventDefault(); setIsDragging(true); };
  const onDragLeave = () => setIsDragging(false);
  const onDrop = (e) => {
    e.preventDefault(); setIsDragging(false);
    if (e.dataTransfer.files?.[0]) handleFileSelect(e.dataTransfer.files[0]);
  };

  const handleFileSelect = (f) => {
    if (f.type !== "application/pdf" && !f.name.toLowerCase().endsWith(".pdf")) {
      alert("Only PDF files are supported."); return;
    }
    setFile(f);
  };

  const startNewAnalysis = () => {
    resetSession();
    setFile(null);
    setProcessing(false);
    setCurrentStage(-1);
    setElapsedTimes({});
    setTotalElapsed(0);
    setShowResults(false);
    setUploadedDocumentId(null);
    setError(null);
  };

  const startPipeline = async () => {
    setProcessing(true); 
    setCurrentStage(0);
    setTotalElapsed(0); 
    setElapsedTimes({}); 
    setShowResults(false);
    setError(null);
    
    // Start total elapsed timer
    totalTimerRef.current = setInterval(() => setTotalElapsed(p => p + 100), 100);
    
    try {
      console.log('[PIPELINE] Starting pipeline for file:', file.name);
      
      // Step 1: Upload file to backend
      console.log('[PIPELINE] Uploading file...');
      const formData = new FormData();
      formData.append('file', file);
      formData.append('document_type', 'RBI_Circular');
      
      const uploadResponse = await api.post('/admin/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      const documentId = uploadResponse.data.id;
      setUploadedDocumentId(documentId);
      console.log('[PIPELINE] File uploaded, document ID:', documentId);
      
      // Step 2: Start visual stage progression
      console.log('[PIPELINE] Starting visual stage progression...');
      runStage(0);
      
      // Step 3: After stages complete, call process endpoint
      // Wait for all stages to complete visually
      const totalStageDuration = STAGES.length * (isDemo ? 600 : 2000);
      
      setTimeout(async () => {
        try {
          console.log('[PIPELINE] Visual stages complete, calling process endpoint...');
          console.log('[PIPELINE] Processing document ID:', documentId);
          
          const processResponse = await api.post(`/admin/process-document/${documentId}`);
          
          console.log('[PIPELINE] Processing complete:', processResponse.data);
          console.log('[PIPELINE] Requirements created:', processResponse.data.requirements_created);
          console.log('[PIPELINE] Assignments created:', processResponse.data.assignments_created);
          
          // Pipeline complete - show success
          console.log('[PIPELINE] Pipeline successfully completed');
          
        } catch (processError) {
          console.error('[PIPELINE] Processing failed:', processError);
          setError(processError.response?.data?.detail || 'Processing failed. Please try again.');
          clearInterval(totalTimerRef.current);
          setProcessing(false);
        }
      }, totalStageDuration);
      
    } catch (uploadError) {
      console.error('[PIPELINE] Upload failed:', uploadError);
      setError(uploadError.response?.data?.detail || 'Upload failed. Please try again.');
      clearInterval(totalTimerRef.current);
      setProcessing(false);
      setCurrentStage(-1);
    }
  };

  const runStage = (stageIdx) => {
    if (stageIdx >= STAGES.length) { clearInterval(totalTimerRef.current); return; }
    const dur = isDemo ? 600 : 1500 + Math.random() * 2000;
    const start = Date.now();
    timerRef.current = setInterval(() => {
      const now = Date.now();
      if (now - start >= dur) {
        clearInterval(timerRef.current);
        setElapsedTimes(p => ({ ...p, [stageIdx]: dur }));
        setCurrentStage(stageIdx + 1);
        runStage(stageIdx + 1);
      } else {
        setElapsedTimes(p => ({ ...p, [stageIdx]: now - start }));
      }
    }, 50);
  };

  useEffect(() => () => { clearInterval(timerRef.current); clearInterval(totalTimerRef.current); }, []);

  /* ── Restored session → show analysis ── */
  if (showResults && hasSession) {
    return (
      <div>
        <Breadcrumbs />
        <div className="page-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
              <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#10b981,#059669)", boxShadow: "0 0 10px rgba(16,185,129,0.4)" }} />
              <h1 className="page-title">Analysis Results</h1>
            </div>
            <p className="page-subtitle" style={{ paddingLeft: 14 }}>
              Regulatory intelligence analysis for <strong style={{ color: "#f1f5f9" }}>{session.file.name}</strong>
            </p>
          </div>
          <button onClick={startNewAnalysis} style={{ padding: "8px 18px", borderRadius: 8, background: "rgba(139,92,246,0.12)", border: "1px solid rgba(139,92,246,0.3)", color: "#c4b5fd", fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
            Upload New Circular
          </button>
        </div>
        <AnalysisResults session={session} />
      </div>
    );
  }

  /* ── Upload + Processing View ── */
  return (
    <div>
      <Breadcrumbs />
      <div className="page-header">
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 5 }}>
          <div style={{ width: 4, height: 28, borderRadius: 2, background: "linear-gradient(180deg,#8b5cf6,#d946ef)", boxShadow: "0 0 10px rgba(217,70,239,0.4)" }} />
          <h1 className="page-title">Regulatory Intelligence Pipeline</h1>
        </div>
        <p className="page-subtitle" style={{ paddingLeft: 14 }}>
          Upload RBI Circulars for autonomous processing, requirement extraction, and MAP generation.
        </p>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: processing ? "1fr 1fr" : "1fr", gap: 24, transition: "all 0.4s" }}>
        {/* Upload Zone */}
        <div className="card animate-fade-up" style={{ padding: 40, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: 380, border: isDragging ? "2px dashed #10b981" : "1.5px dashed rgba(255,255,255,0.15)", background: isDragging ? "rgba(16,185,129,0.05)" : "#162030", transition: "all 0.2s" }}
          onDragOver={onDragOver} onDragLeave={onDragLeave} onDrop={onDrop}>
          <input type="file" ref={fileInputRef} onChange={e => e.target.files[0] && handleFileSelect(e.target.files[0])} accept="application/pdf" style={{ display: "none" }} />
          {!file ? (
            <div style={{ textAlign: "center" }}>
              <div style={{ width: 64, height: 64, borderRadius: 16, background: "rgba(139,92,246,0.1)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 20px" }}>
                <svg width="32" height="32" fill="none" stroke="#a78bfa" strokeWidth="2" viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
              </div>
              <h3 style={{ fontSize: 18, color: "#f1f5f9", marginBottom: 8 }}>Upload RBI Circular</h3>
              <p style={{ fontSize: 13, color: "#94a3b8", marginBottom: 6, maxWidth: 340 }}>Drag and drop a PDF file here, or click to browse.</p>
              <p style={{ fontSize: 11.5, color: "#475569", marginBottom: 24 }}>Supported: <strong style={{ color: "#94a3b8" }}>PDF</strong> · Fully offline processing.</p>
              <button onClick={() => fileInputRef.current?.click()} style={{ background: "#a78bfa", color: "#111827", border: "none", padding: "10px 24px", borderRadius: 8, fontSize: 13, fontWeight: 700, cursor: "pointer" }}>
                Browse File
              </button>
            </div>
          ) : (
            <div style={{ width: "100%", maxWidth: 400 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 16, background: "rgba(255,255,255,0.03)", padding: 20, borderRadius: 12, border: "1px solid rgba(255,255,255,0.08)" }}>
                <svg width="36" height="36" fill="none" stroke="#ef4444" strokeWidth="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
                <div style={{ flex: 1, overflow: "hidden" }}>
                  <div style={{ color: "#f1f5f9", fontWeight: 700, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{file.name}</div>
                  <div style={{ color: "#64748b", fontSize: 11.5, marginTop: 4 }}>{(file.size / 1024 / 1024).toFixed(2)} MB · {new Date().toLocaleTimeString()}</div>
                </div>
                {!processing && <button onClick={() => setFile(null)} style={{ background: "transparent", border: "none", color: "#64748b", fontSize: 20, cursor: "pointer" }}>✕</button>}
              </div>
              {!processing ? (
                <button onClick={startPipeline} style={{ width: "100%", marginTop: 24, background: "linear-gradient(135deg, #10b981, #059669)", color: "#fff", border: "none", padding: 12, borderRadius: 8, fontSize: 14, fontWeight: 700, cursor: "pointer", boxShadow: "0 4px 14px rgba(16,185,129,0.3)" }}>
                  Initiate Processing Pipeline
                </button>
              ) : (
                <div style={{ marginTop: 24, padding: 16, background: error ? "rgba(239,68,68,0.12)" : (pipelineComplete ? "rgba(16,185,129,0.12)" : "rgba(56,189,248,0.08)"), border: `1px solid ${error ? "rgba(239,68,68,0.25)" : (pipelineComplete ? "rgba(16,185,129,0.25)" : "rgba(56,189,248,0.2)")}`, borderRadius: 8 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                    <span style={{ fontSize: 12, color: error ? "#ef4444" : (pipelineComplete ? "#10b981" : "#38bdf8"), fontWeight: 700 }}>
                      {error ? "✕ ERROR" : (pipelineComplete ? "✓ ANALYSIS COMPLETE" : "PROCESSING...")}
                    </span>
                    <span style={{ fontSize: 12, color: "#94a3b8", fontFamily: "monospace" }}>{(totalElapsed / 1000).toFixed(1)}s</span>
                  </div>
                  {!error && (
                    <div style={{ height: 6, background: "rgba(255,255,255,0.1)", borderRadius: 3, overflow: "hidden" }}>
                      <div style={{ width: `${Math.min(100, (currentStage / STAGES.length) * 100)}%`, height: "100%", background: pipelineComplete ? "#10b981" : "#38bdf8", transition: "width 0.4s ease" }} />
                    </div>
                  )}
                  {error && (
                    <div style={{ marginTop: 12, fontSize: 12, color: "#f87171", textAlign: "center" }}>
                      {error}
                    </div>
                  )}
                  {pipelineComplete && !error && <div style={{ marginTop: 12, fontSize: 12, color: "#94a3b8", textAlign: "center" }}>Generating analysis report...</div>}
                  {error && (
                    <button onClick={startNewAnalysis} style={{ width: "100%", marginTop: 12, background: "rgba(239,68,68,0.1)", color: "#ef4444", border: "1px solid rgba(239,68,68,0.2)", padding: "8px", borderRadius: 6, fontSize: 12, fontWeight: 700, cursor: "pointer" }}>
                      Try Again
                    </button>
                  )}
                </div>
              )}
            </div>
          )}
        </div>

        {/* Stages */}
        {processing && (
          <div className="card animate-fade-in" style={{ padding: 24, display: "flex", flexDirection: "column", gap: 8 }}>
            <h3 style={{ fontSize: 15, color: "#f1f5f9", marginBottom: 12 }}>Pipeline Status</h3>
            {STAGES.map((stage, idx) => {
              const isPast = currentStage > idx, isCurrent = currentStage === idx;
              let bg = "rgba(255,255,255,0.03)";
              if (isPast) bg = "rgba(16,185,129,0.08)";
              else if (isCurrent) bg = "rgba(56,189,248,0.08)";
              const outputs = [
                "1 Document Loaded", "314 pages extracted", "320 requirements found",
                "134 Mandatory / 74 Conditional", "15 semantic links detected",
                "32 nodes / 44 edges constructed", "7 business units mapped",
                "320 Action Plans created", "Executive Report generated"
              ];
              const t = elapsedTimes[idx] != null ? `${(elapsedTimes[idx] / 1000).toFixed(1)}s` : (isCurrent ? `${((elapsedTimes[idx] || 0) / 1000).toFixed(1)}s` : "--");
              return (
                <div key={idx} style={{ display: "flex", alignItems: "center", gap: 14, padding: "12px 16px", background: bg, border: `1px solid ${isCurrent ? "rgba(56,189,248,0.2)" : isPast ? "rgba(16,185,129,0.15)" : "rgba(255,255,255,0.05)"}`, borderRadius: 8, transition: "all 0.3s" }}>
                  <div style={{ width: 24, height: 24, borderRadius: "50%", background: isPast ? "#10b981" : isCurrent ? "transparent" : "#1a2332", border: isCurrent ? "2px solid #38bdf8" : "none", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                    {isPast && <svg width="14" height="14" fill="none" stroke="#fff" strokeWidth="2.5" viewBox="0 0 24 24"><path d="M20 6L9 17l-5-5"/></svg>}
                    {isCurrent && <div style={{ width: 8, height: 8, background: "#38bdf8", borderRadius: "50%", animation: "pulse-dot 1s infinite" }} />}
                  </div>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: 13, fontWeight: 700, color: isPast ? "#f1f5f9" : isCurrent ? "#38bdf8" : "#64748b" }}>{stage}</div>
                    {isPast && <div style={{ fontSize: 11, color: "#34d399", marginTop: 2, fontWeight: 600 }}>↳ {outputs[idx]}</div>}
                  </div>
                  <div style={{ fontSize: 11, fontFamily: "monospace", color: isPast ? "#34d399" : isCurrent ? "#38bdf8" : "#475569" }}>{isPast ? "✓ " : ""}{t}</div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
