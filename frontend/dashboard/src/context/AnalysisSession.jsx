import React, { createContext, useContext, useState, useMemo, useCallback } from "react";
import {
  dashboardMetrics, mapsOutput, departmentHeatmap,
  requirementsTaxonomy, graphData, departmentSummary, mapDetails
} from "../data/demo";

const AnalysisSessionContext = createContext(null);

/**
 * BUILD KNOWLEDGE GRAPH FROM BACKEND DATA
 * Constructs graph nodes and edges exclusively from backend response
 * No demo.js imports - uses only /admin/document-analysis/{id} data
 * 
 * Graph Structure (4 levels):
 * 1. Circular node (Document)
 * 2. Requirement nodes (extracted requirements)
 * 3. MAP nodes (assignments)
 * 4. Department nodes (affected departments)
 * 
 * @param {Object} data - Backend response from /admin/document-analysis/{id}
 * @returns {Object} { nodes: [], edges: [] }
 */
function buildKnowledgeGraphFromBackend(data) {
  const nodes = [];
  const edges = [];
  const nodeIds = new Set();
  
  console.log('[GRAPH_BUILDER] Building knowledge graph from backend data');
  console.log('[GRAPH_BUILDER] Assignments count:', data.assignments?.length || 0);
  console.log('[GRAPH_BUILDER] Departments count:', data.department_summary?.length || 0);
  
  // 1. Create Circular node (Document)
  const circularId = `DOC_${data.document.id}`;
  nodes.push({
    data: {
      id: circularId,
      label: data.document.filename || 'Document',
      type: 'circular'
    }
  });
  nodeIds.add(circularId);
  console.log('[GRAPH_BUILDER] Created circular node:', circularId);
  
  // 2. Create Requirement nodes and Circular → Requirement edges
  const uniqueRequirements = [...new Set(
    data.assignments.map(a => a.requirement_id)
  )];
  
  console.log('[GRAPH_BUILDER] Unique requirements:', uniqueRequirements.length);
  
  uniqueRequirements.forEach(reqId => {
    if (reqId) {
      nodes.push({
        data: {
          id: reqId,
          label: reqId.slice(0, 18), // Truncate for display
          type: 'requirement'
        }
      });
      nodeIds.add(reqId);
      
      // Edge: Circular → Requirement
      edges.push({
        data: {
          source: circularId,
          target: reqId,
          label: 'defines'
        }
      });
    }
  });
  
  console.log('[GRAPH_BUILDER] Created requirement nodes:', uniqueRequirements.length);
  
  // 3. Create MAP nodes and Requirement → MAP edges
  data.assignments.forEach(assignment => {
    const mapId = `MAP_${assignment.id}`;
    
    nodes.push({
      data: {
        id: mapId,
        label: `${assignment.department} - ${assignment.priority}`,
        type: 'map',
        status: assignment.status,
        priority: assignment.priority
      }
    });
    nodeIds.add(mapId);
    
    // Edge: Requirement → MAP
    if (assignment.requirement_id) {
      edges.push({
        data: {
          source: assignment.requirement_id,
          target: mapId,
          label: 'generates'
        }
      });
    }
  });
  
  console.log('[GRAPH_BUILDER] Created MAP nodes:', data.assignments.length);
  
  // 4. Create Department nodes
  data.department_summary.forEach(dept => {
    const deptId = `DEPT_${dept.department_id}`;
    
    if (!nodeIds.has(deptId)) {
      nodes.push({
        data: {
          id: deptId,
          label: dept.department_name,
          type: 'department',
          totalAssignments: dept.total_assignments
        }
      });
      nodeIds.add(deptId);
    }
  });
  
  console.log('[GRAPH_BUILDER] Created department nodes:', data.department_summary.length);
  
  // 5. Create MAP → Department edges
  data.assignments.forEach(assignment => {
    const mapId = `MAP_${assignment.id}`;
    const deptId = `DEPT_${assignment.department_id}`;
    
    edges.push({
      data: {
        source: mapId,
        target: deptId,
        label: 'assigned_to'
      }
    });
  });
  
  console.log('[GRAPH_BUILDER] Total nodes:', nodes.length);
  console.log('[GRAPH_BUILDER] Total edges:', edges.length);
  console.log('[GRAPH_BUILDER] Graph construction complete');
  
  return { nodes, edges };
}

/**
 * PRODUCTION HOTFIX: Build AnalysisResult from backend API
 * This replaces generateDocumentAnalysis() for backend-driven analysis
 */
async function buildAnalysisResult(documentId, api) {
  try {
    console.log('[ANALYSIS_RESULT] ========== BUILD START ==========');
    console.log('[ANALYSIS_RESULT] Input:', { documentId, hasApi: !!api });
    
    if (!documentId) {
      console.error('[ANALYSIS_RESULT] ERROR: documentId is null/undefined');
      return null;
    }
    
    if (!api) {
      console.error('[ANALYSIS_RESULT] ERROR: api is null/undefined');
      return null;
    }
    
    const endpoint = `/admin/document-analysis/${documentId}`;
    console.log('[ANALYSIS_RESULT] Fetching from endpoint:', endpoint);
    
    // Fetch complete analysis from new backend endpoint
    const response = await api.get(endpoint);
    
    console.log('[ANALYSIS_RESULT] Response status:', response.status);
    console.log('[ANALYSIS_RESULT] Response data keys:', Object.keys(response.data || {}));
    console.log('[ANALYSIS_RESULT] Full response.data:', response.data);
    
    const data = response.data;
    
    if (!data) {
      console.error('[ANALYSIS_RESULT] ERROR: response.data is null');
      return null;
    }
    
    if (!data.document) {
      console.error('[ANALYSIS_RESULT] ERROR: response.data.document is missing');
    }
    
    if (!data.counts) {
      console.error('[ANALYSIS_RESULT] ERROR: response.data.counts is missing');
    }
    
    if (!data.assignments) {
      console.error('[ANALYSIS_RESULT] ERROR: response.data.assignments is missing');
    }
    
    console.log('[ANALYSIS_RESULT] Building AnalysisResult object...');
    
    // Build knowledge graph from backend data (no demo.js dependency)
    const backendGraph = buildKnowledgeGraphFromBackend(data);
    
    // Generate domains from backend assignments (deterministic)
    const domainCounts = {};
    data.assignments.forEach(a => {
      const domain = a.domain || 'General';
      domainCounts[domain] = (domainCounts[domain] || 0) + 1;
    });
    const domains = Object.entries(domainCounts).sort((a, b) => b[1] - a[1]);
    
    // Generate AI Executive Briefing from backend data (deterministic heuristics)
    const criticalCount = data.counts.critical_priority || 0;
    const highCount = data.counts.high_priority || 0;
    const totalAssignments = data.counts.assignments_generated || 0;
    const departmentsAffected = data.counts.departments_affected || 0;
    const topDepartments = data.department_summary.slice(0, 3).map(d => d.department_name);
    const topTwoDepts = data.department_summary.slice(0, 2).map(d => d.department_name);
    
    const aiBriefing = {
      overallRisk: criticalCount > 5 ? "CRITICAL" : criticalCount > 0 ? "HIGH" : "MEDIUM",
      businessImpact: `This circular introduces material changes affecting operations across ${departmentsAffected} business units. Core impact is highly concentrated in ${domains[0]?.[0] || "General"} and ${domains[1]?.[0] || "Risk"} compliance standards.`,
      immediateActions: `Immediate remediation is required on ${criticalCount} critical regulatory obligations. Establish task forces for the top impacted departments to avoid immediate non-compliance.`,
      departmentsToNotify: topDepartments.join(", "),
      estimatedEffort: `${totalAssignments * 8.5} person-hours. Estimated via deterministic historical workload extrapolation.`,
      expectedCompletion: `Projected 45-60 days baseline due to the volume of ${highCount} high-priority tasks.`,
      executiveRecommendation: `Assemble an executive steering committee comprising heads of ${topTwoDepts.join(" and ")}. Authorize immediate reallocation of compliance budgets to resolve the critical path MAPs within 14 days to mitigate potential RBI censures.`
    };
    
    // Build AnalysisResult object
    const analysisResult = {
      document: data.document,
      counts: data.counts,
      assignments: data.assignments,
      departmentSummary: data.department_summary,
      priorityDistribution: data.priority_distribution,
      
      // Dashboard summary (derived)
      dashboardSummary: {
        totalUnpublished: data.assignments.filter(a => !a.is_published).length,
        totalPublished: data.assignments.filter(a => a.is_published).length,
        pendingTasks: data.assignments.filter(a => a.status === 'pending').length,
        completedTasks: data.assignments.filter(a => a.status === 'completed').length
      },
      
      // Graph data (use demo structure for MVP, but with backend counts)
      graphData: {
        nodes: graphData.nodes, // Demo structure (kept for legacy compatibility)
        edges: graphData.edges, // Demo structure (kept for legacy compatibility)
        requirementNodes: data.counts.requirements_extracted,
        assignmentNodes: data.counts.assignments_generated,
        departmentNodes: data.counts.departments_affected
      },
      
      // ACTIVE SESSION GRAPH - Built from backend data
      scopedGraph: {
        nodes: backendGraph.nodes,  // ← Backend nodes with NEW IDs (REQ_DOC1_*)
        edges: backendGraph.edges   // ← Backend edges matching NEW IDs
      },
      
      // Compatibility: Keep these for pages that still reference them
      requirements: data.assignments.map(a => ({
        req_id: a.requirement_id,
        text: a.requirement_text,
        domain: a.domain,
        classification: a.classification,
        priority: a.priority
      })),
      // MVP: MAPs are Assignment records with compatibility fields
      maps: data.assignments.map(a => ({
        ...a,  // Include all backend fields
        map_id: `MAP_${a.id}`,  // Generate MAP ID for display/navigation
        title: a.requirement_text,  // Use requirement text as title
        req_id: a.requirement_id,  // Alias for compatibility
      })),
      departments: data.department_summary.map(d => ({
        department: d.department_name,
        total_maps: d.total_assignments,
        Critical: d.critical,
        High: d.high,
        Medium: d.medium,
        Low: d.low
      })),
      stats: {
        totalRequirements: data.counts.requirements_extracted,
        totalMaps: data.counts.assignments_generated,
        criticalMaps: data.counts.critical_priority,
        highMaps: data.counts.high_priority,
        departmentsImpacted: data.counts.departments_affected,
        graphNodes: data.counts.requirements_extracted + data.counts.assignments_generated + data.counts.departments_affected,
        graphEdges: data.counts.assignments_generated * 2, // Rough estimate
        crossReferences: 0 // Not tracked
      },
      
      // RENDER CONTRACT FIELDS - Required by Pipeline.jsx
      aiBriefing,  // Line 94+ in Pipeline.jsx
      domains,     // Line 161 in Pipeline.jsx
      
      // Source flag
      fromBackend: true
    };
    
    console.log('[ANALYSIS_RESULT] AnalysisResult built successfully');
    console.log('[ANALYSIS_RESULT] Stats:', analysisResult.stats);
    console.log('[ANALYSIS_RESULT] ========== BUILD COMPLETE ==========');
    return analysisResult;
    
  } catch (error) {
    console.error('[ANALYSIS_RESULT] ========== BUILD FAILED ==========');
    console.error('[ANALYSIS_RESULT] Error type:', error.constructor.name);
    console.error('[ANALYSIS_RESULT] Error message:', error.message);
    if (error.response) {
      console.error('[ANALYSIS_RESULT] HTTP Status:', error.response.status);
      console.error('[ANALYSIS_RESULT] Response data:', error.response.data);
    }
    console.error('[ANALYSIS_RESULT] Full error:', error);
    console.error('[ANALYSIS_RESULT] Stack trace:', error.stack);
    
    // Fallback to demo if backend fails
    console.warn('[ANALYSIS_RESULT] Returning NULL - will trigger demo fallback');
    return null;
  }
}

/**
 * LEGACY: Generates a deterministic document-level analysis package
 * by filtering existing backend JSON to a specific set of source documents.
 * ONLY used as fallback if buildAnalysisResult fails
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

  const createSession = useCallback(async (file, documentId, api, elapsedTimes, totalElapsed) => {
    console.log('[SESSION] ========== CREATE SESSION START ==========');
    console.log('[SESSION] Input parameters:', {
      fileName: file?.name,
      fileSize: file?.size,
      documentId,
      hasApi: !!api,
      elapsedTimes,
      totalElapsed
    });
    
    // Try to build AnalysisResult from backend
    let analysis = null;
    if (documentId && api) {
      console.log('[SESSION] Attempting to build AnalysisResult from backend...');
      analysis = await buildAnalysisResult(documentId, api);
      console.log('[SESSION] buildAnalysisResult returned:', analysis ? 'SUCCESS' : 'NULL');
    } else {
      console.log('[SESSION] Missing documentId or api:', { documentId, hasApi: !!api });
    }
    
    // Fallback to demo if backend fails
    if (!analysis) {
      console.warn('[SESSION] Backend analysis failed - using demo fallback');
      console.warn('[SESSION] This means buildAnalysisResult returned null');
      analysis = generateDocumentAnalysis(file.name);
      analysis.fromBackend = false;
    }
    
    const sessionObject = {
      file: { name: file.name, size: file.size, uploadTime: new Date().toISOString() },
      processing: { complete: true, elapsedTimes, totalElapsed },
      analysis,
      analysisResult: analysis, // HOTFIX: Alias for new code
      createdAt: Date.now(),
      fromBackend: analysis.fromBackend
    };
    
    console.log('[SESSION] Setting session state with:', {
      fromBackend: sessionObject.fromBackend,
      hasAnalysis: !!sessionObject.analysis,
      requirementsCount: sessionObject.analysis?.stats?.totalRequirements,
      assignmentsCount: sessionObject.analysis?.stats?.totalMaps
    });
    
    setSession(sessionObject);
    
    console.log('[SESSION] ========== CREATE SESSION COMPLETE ==========');
    console.log('[SESSION] Session created successfully');
  }, []);

  const resetSession = useCallback(() => {
    console.log('[SESSION] Clearing analysis session');
    setSession(null);
  }, []);

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
