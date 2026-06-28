import React, { createContext, useContext, useState, useMemo, useCallback } from "react";
import {
  dashboardMetrics, mapsOutput, departmentHeatmap,
  requirementsTaxonomy, graphData, departmentSummary, mapDetails
} from "../data/demo";

const AnalysisSessionContext = createContext(null);

/**
 * Generates a deterministic document-level analysis package
 * by filtering existing backend JSON to a specific set of source documents.
 */
function generateDocumentAnalysis(fileName) {
  // Gather all unique source documents
  const allSources = [...new Set(requirementsTaxonomy.map(r => r.source_document))];

  // Deterministically pick 2-4 source docs based on filename hash
  let hash = 0;
  for (let i = 0; i < fileName.length; i++) hash = ((hash << 5) - hash + fileName.charCodeAt(i)) | 0;
  const idx = Math.abs(hash) % allSources.length;
  const selectedSources = [
    allSources[idx],
    allSources[(idx + 3) % allSources.length],
    allSources[(idx + 7) % allSources.length],
  ];

  // Filter requirements to those source documents
  const docRequirements = requirementsTaxonomy.filter(r => selectedSources.includes(r.source_document));

  // Get requirement IDs for MAP linkage
  const docReqIds = new Set(docRequirements.map(r => r.req_id));

  // Filter MAPs linked to these requirements via mapDetails
  const docMapIds = [];
  const docMapEntries = [];
  for (const m of mapsOutput) {
    const detail = mapDetails[m.map_id];
    if (detail && docReqIds.has(detail.source_requirement?.req_id)) {
      docMapIds.push(m.map_id);
      docMapEntries.push(m);
    }
  }
  // If we got very few maps, also include maps whose source_document matches
  if (docMapEntries.length < 20) {
    for (const m of mapsOutput) {
      const detail = mapDetails[m.map_id];
      if (detail && selectedSources.includes(detail.source_requirement?.source_document) && !docMapIds.includes(m.map_id)) {
        docMapIds.push(m.map_id);
        docMapEntries.push(m);
      }
    }
  }

  // Compute department breakdown from document MAPs
  const standardDepartments = [
    "Compliance", "Risk Management", "Treasury", "Operations", 
    "Cyber Security", "IT", "Finance", "AML", "Legal"
  ];
  const deptMap = {};
  for (const name of standardDepartments) {
    deptMap[name] = { total: 0, Critical: 0, High: 0, Medium: 0, Low: 0, impactSum: 0 };
  }
  for (const m of docMapEntries) {
    if (deptMap[m.department]) {
      deptMap[m.department].total++;
      deptMap[m.department][m.priority] = (deptMap[m.department][m.priority] || 0) + 1;
      deptMap[m.department].impactSum += m.impact_score;
    }
  }
  const docDepartments = Object.entries(deptMap).map(([name, d]) => ({
    department: name, total_maps: d.total,
    Critical: d.Critical, High: d.High, Medium: d.Medium, Low: d.Low,
    avg_impact: d.total ? (d.impactSum / d.total).toFixed(1) : 0,
    confidence: departmentSummary.find(ds => ds.department === name)?.total_risk_score > 5000 ? "High" : "Medium",
  })).sort((a, b) => b.total_maps - a.total_maps);

  // Domain breakdown
  const domainMap = {};
  for (const r of docRequirements) {
    domainMap[r.domain] = (domainMap[r.domain] || 0) + 1;
  }
  const domains = Object.entries(domainMap).sort((a, b) => b[1] - a[1]);

  // Obligation type breakdown
  const obligationMap = {};
  for (const r of docRequirements) {
    // We have domain/subdomain but obligation_type is in raw JSON. Derive proportionally.
  }

  // Build a scoped knowledge graph
  const scopedNodes = [];
  const scopedEdges = [];
  const nodeIdSet = new Set();

  // 1. Circular node (Use exactly the filename for perfect deduplication)
  const circularId = fileName;
  scopedNodes.push({ data: { id: circularId, label: fileName.replace(".pdf", ""), type: "circular" } });
  nodeIdSet.add(circularId);

  // 2. Select MAPs first to ensure lineage (up to 12 for readability)
  const graphMaps = docMapEntries.slice(0, 12);

  // 3. Find EXACT requirements for those MAPs
  const requiredReqIds = new Set();
  for (const m of graphMaps) {
    const detail = mapDetails[m.map_id];
    if (detail && detail.source_requirement?.req_id) {
      requiredReqIds.add(detail.source_requirement.req_id);
    }
  }

  // 4. Add those Requirements and link strictly to the Circular node
  for (const reqId of requiredReqIds) {
    scopedNodes.push({ data: { id: reqId, label: reqId.slice(0, 18), type: "requirement" } });
    nodeIdSet.add(reqId);
    scopedEdges.push({ data: { source: circularId, target: reqId, label: "defines" } });
  }

  // 5. Add MAPs and link strictly to their Requirements
  for (const m of graphMaps) {
    scopedNodes.push({ data: { id: m.map_id, label: m.map_id.slice(0, 16), type: "map" } });
    nodeIdSet.add(m.map_id);
    const detail = mapDetails[m.map_id];
    if (detail && nodeIdSet.has(detail.source_requirement?.req_id)) {
      scopedEdges.push({ data: { source: detail.source_requirement.req_id, target: m.map_id, label: "generates" } });
    }
  }

  // 6. Add Departments and link strictly to MAPs
  const deptNames = new Set(graphMaps.map(m => m.department));
  for (const deptName of deptNames) {
    const deptId = `dept_${deptName.replace(/[^a-zA-Z0-9]/g, "_")}`;
    scopedNodes.push({ data: { id: deptId, label: deptName, type: "department" } });
    nodeIdSet.add(deptId);
  }
  for (const m of graphMaps) {
    const deptId = `dept_${m.department.replace(/[^a-zA-Z0-9]/g, "_")}`;
    scopedEdges.push({ data: { source: m.map_id, target: deptId, label: "assigned" } });
  }

  // Generate AI Executive Briefing
  const aiBriefing = {
    overallRisk: docMapEntries.filter(m => m.priority === "Critical").length > 5 ? "CRITICAL" : docMapEntries.filter(m => m.priority === "Critical").length > 0 ? "HIGH" : "MEDIUM",
    businessImpact: `This circular introduces material changes affecting operations across ${docDepartments.length} business units. Core impact is highly concentrated in ${domains[0]?.[0] || "General"} and ${domains[1]?.[0] || "Risk"} compliance standards.`,
    immediateActions: `Immediate remediation is required on ${docMapEntries.filter(m => m.priority === "Critical").length} critical regulatory obligations. Establish task forces for the top impacted departments to avoid immediate non-compliance.`,
    departmentsToNotify: docDepartments.slice(0, 3).map(d => d.department).join(", "),
    estimatedEffort: `${docMapEntries.length * 8.5} person-hours. Estimated via deterministic historical workload extrapolation.`,
    expectedCompletion: `Projected 45-60 days baseline due to the volume of ${docMapEntries.filter(m => m.priority === "High").length} high-priority tasks.`,
    executiveRecommendation: `Assemble an executive steering committee comprising heads of ${docDepartments.slice(0, 2).map(d => d.department).join(" and ")}. Authorize immediate reallocation of compliance budgets to resolve the critical path MAPs within 14 days to mitigate potential RBI censures.`
  };

  return {
    fileName,
    selectedSources,
    requirements: docRequirements,
    maps: docMapEntries,
    mapIds: new Set(docMapIds),
    departments: docDepartments,
    domains,
    scopedGraph: { nodes: scopedNodes, edges: scopedEdges },
    stats: {
      totalRequirements: docRequirements.length,
      totalMaps: docMapEntries.length,
      criticalMaps: docMapEntries.filter(m => m.priority === "Critical").length,
      highMaps: docMapEntries.filter(m => m.priority === "High").length,
      departmentsImpacted: docDepartments.length,
      graphNodes: scopedNodes.length,
      graphEdges: scopedEdges.length,
      crossReferences: scopedEdges.filter(e => e.data.label === "defines").length,
    },
    aiBriefing
  };
}

export function AnalysisSessionProvider({ children }) {
  const [session, setSession] = useState(null);

  const createSession = useCallback((file, elapsedTimes, totalElapsed) => {
    const analysis = generateDocumentAnalysis(file.name);
    setSession({
      file: { name: file.name, size: file.size, uploadTime: new Date().toISOString() },
      processing: { complete: true, elapsedTimes, totalElapsed },
      analysis,
      createdAt: Date.now(),
    });
  }, []);

  const resetSession = useCallback(() => setSession(null), []);

  const downloadReport = useCallback((type, data = null) => {
    if (!session) return;
    let content = "";
    let filename = "";
    if (type === "Executive") {
      filename = `Executive_Report_${session.file.name}.txt`;
      content = `EXECUTIVE COMPLIANCE REPORT\nDocument: ${session.file.name}\nDate: ${new Date().toLocaleString()}\n\n`;
      content += `OVERALL RISK: ${session.analysis.aiBriefing.overallRisk}\n`;
      content += `BUSINESS IMPACT: ${session.analysis.aiBriefing.businessImpact}\n\n`;
      content += `EXECUTIVE RECOMMENDATION:\n${session.analysis.aiBriefing.executiveRecommendation}\n\n`;
      content += `STATISTICS:\n- Requirements: ${session.analysis.stats.totalRequirements}\n- MAPs: ${session.analysis.stats.totalMaps}\n- Departments Impacted: ${session.analysis.stats.departmentsImpacted}\n`;
    } else if (type === "Department" && data) {
      filename = `Department_Report_${data.department}.txt`;
      content = `DEPARTMENT COMPLIANCE REPORT\nDepartment: ${data.department}\nDocument: ${session.file.name}\n\n`;
      content += `Total MAPs: ${data.total_maps}\nCritical: ${data.Critical}\nHigh: ${data.High}\n\n`;
      content += `AI RECOMMENDATION:\nImmediate action required on ${data.Critical} critical tasks. Reallocate resources to meet the compliance deadline.\n`;
    } else if (type === "MAP" && data) {
      filename = `MAP_Report_${data.map_id}.txt`;
      content = `MITIGATION ACTION PLAN REPORT\nMAP ID: ${data.map_id}\nPriority: ${data.priority}\nDepartment: ${data.department}\nDeadline: ${data.deadline}\n\n`;
      content += `Task: ${data.title}\n\n`;
      content += `AI REASONING:\nThis MAP was generated because it maps to a critical operational requirement derived from ${session.file.name}. Failure to execute poses high operational risk.\n`;
    } else if (type === "Requirement" && data) {
      filename = `Requirement_Report_${data.req_id}.txt`;
      content = `REQUIREMENT REPORT\nReq ID: ${data.req_id}\nDomain: ${data.domain}\n\n`;
      content += `Text: ${data.text}\n\n`;
      content += `AI CLASSIFICATION REASONING:\nClassified under ${data.domain} due to strong semantic proximity to established regulatory frameworks.\n`;
    }

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }, [session]);

  const value = useMemo(() => ({
    session, createSession, resetSession, downloadReport, hasSession: !!session,
  }), [session, createSession, resetSession, downloadReport]);

  return (
    <AnalysisSessionContext.Provider value={value}>
      {children}
    </AnalysisSessionContext.Provider>
  );
}

export function useAnalysisSession() {
  const ctx = useContext(AnalysisSessionContext);
  if (!ctx) throw new Error("useAnalysisSession must be used within AnalysisSessionProvider");
  return ctx;
}
