import dashboardMetricsRaw from './dashboard_metrics.json';
import mapsOutputRaw from './maps_output.json';
import departmentSummaryRaw from './department_summary.json';
import departmentHeatmapRaw from './department_heatmap.json';
import requirementsTaxonomyRaw from './requirements_taxonomy.json';
import referenceGraphV2Raw from './reference_graph_v2.json';
import mapDetailsRaw from './map_details.json';
import topRiskDepartmentsRaw from './top_risk_departments.json';
import prioritySummaryRaw from './priority_summary.json';
import executiveSummaryRaw from './executive_summary.json';

// mapsOutput transformation
export const mapsOutput = mapsOutputRaw.map(m => ({
  map_id: m.map_id,
  title: m.task_title,
  department: m.department,
  priority: m.priority,
  impact_score: m.impact_score,
  deadline: m.deadline === "TBD" ? "2026-12-31" : (m.deadline === "three months" ? "2026-09-30" : "2026-12-31"),
  status: m.status || "Pending"
}));

// dashboardMetrics transformation
export const dashboardMetrics = {
  total_requirements: executiveSummaryRaw.total_requirements || 2941,
  total_maps: dashboardMetricsRaw.total_maps,
  critical_maps: dashboardMetricsRaw.critical_maps,
  high_priority_maps: dashboardMetricsRaw.high_maps,
  departments_impacted: dashboardMetricsRaw.departments_impacted,
  upcoming_deadlines: dashboardMetricsRaw.upcoming_deadlines,
  compliance_summary: {
    pending: dashboardMetricsRaw.compliance_summary?.pending_tasks || 2941,
    in_progress: dashboardMetricsRaw.compliance_summary?.in_progress_tasks || 0,
    completed: dashboardMetricsRaw.compliance_summary?.completed_tasks || 0,
    overdue: dashboardMetricsRaw.compliance_summary?.overdue_tasks || 0
  },
  priority_distribution: prioritySummaryRaw,
  top_risk_departments: topRiskDepartmentsRaw
};

// departmentSummary transformation
export const departmentSummary = Object.keys(departmentSummaryRaw).map(k => ({
  department: k,
  total_maps: departmentSummaryRaw[k],
  total_risk_score: topRiskDepartmentsRaw.find(d => d.department === k)?.risk_score || 0,
  critical_count: departmentHeatmapRaw[k]?.critical || 0
}));

// departmentHeatmap transformation
export const departmentHeatmap = Object.keys(departmentHeatmapRaw).map(k => ({
  department: k,
  Critical: departmentHeatmapRaw[k].critical,
  High: departmentHeatmapRaw[k].high,
  Medium: departmentHeatmapRaw[k].medium,
  Low: departmentHeatmapRaw[k].low
}));

// requirementsTaxonomy transformation
export const requirementsTaxonomy = requirementsTaxonomyRaw.map(r => ({
  req_id: r.requirement_id,
  domain: r.domain,
  subdomain: r.subdomain,
  source_document: r.source_document,
  text: r.requirement_text
}));

// Build a representative global graph (sampling to prevent UI lag)
const globalNodes = [];
const globalEdges = [];
const globalNodeIds = new Set();

// 1. All Circulars
const allSources = [...new Set(requirementsTaxonomyRaw.map(r => r.source_document))].filter(Boolean);
for (const src of allSources) {
  globalNodes.push({ data: { id: src, label: src.replace(".pdf", ""), type: "circular" } });
  globalNodeIds.add(src);
}

// 2. Sample ~40 MAPs evenly distributed
const sampleMaps = [];
for (let i = 0; i < mapsOutputRaw.length; i += Math.floor(mapsOutputRaw.length / 40)) {
  if (sampleMaps.length < 40) sampleMaps.push(mapsOutputRaw[i]);
}

// 3. Add Requirements for those MAPs and link to Circulars
const reqsForMaps = new Set();
for (const m of sampleMaps) {
  if (m.requirement_id) reqsForMaps.add(m.requirement_id);
}
for (const reqId of reqsForMaps) {
  const req = requirementsTaxonomyRaw.find(r => r.requirement_id === reqId);
  if (req && req.source_document && globalNodeIds.has(req.source_document)) {
    globalNodes.push({ data: { id: reqId, label: reqId.slice(0, 18), type: "requirement" } });
    globalNodeIds.add(reqId);
    globalEdges.push({ data: { source: req.source_document, target: reqId, label: "defines" } });
  }
}

// 4. Add MAPs and link to Reqs
for (const m of sampleMaps) {
  if (globalNodeIds.has(m.requirement_id)) {
    globalNodes.push({ data: { id: m.map_id, label: m.map_id.slice(0, 16), type: "map" } });
    globalNodeIds.add(m.map_id);
    globalEdges.push({ data: { source: m.requirement_id, target: m.map_id, label: "generates" } });
  }
}

// 5. Add Departments and link to MAPs
const globalDepts = [...new Set(sampleMaps.map(m => m.department))];
for (const dept of globalDepts) {
  const deptId = `dept_${dept.replace(/[^a-zA-Z0-9]/g, "_")}`;
  globalNodes.push({ data: { id: deptId, label: dept, type: "department" } });
  globalNodeIds.add(deptId);
}
for (const m of sampleMaps) {
  if (globalNodeIds.has(m.map_id)) {
    const deptId = `dept_${m.department.replace(/[^a-zA-Z0-9]/g, "_")}`;
    globalEdges.push({ data: { source: m.map_id, target: deptId, label: "assigned" } });
  }
}

export const graphData = { nodes: globalNodes, edges: globalEdges };

// Pre-compute mapsOutput Map for O(1) lookups
const mapsOutputMap = new Map();
mapsOutputRaw.forEach(m => mapsOutputMap.set(m.map_id, m));

// mapDetails transformation
export const mapDetails = {};
mapDetailsRaw.forEach(m => {
  mapDetails[m.map_id] = {
    map_id: m.map_id,
    title: m.task_title,
    priority: m.priority,
    impact_score: m.impact_score,
    status: m.status || "Pending",
    department: { name: m.department, confidence: m.department_confidence, keywords: m.matched_keywords },
    source_requirement: {
      req_id: m.requirement_id,
      text: m.source_requirement,
      source_document: m.source_document,
      domain: m.domain || "Unknown",
      subdomain: m.subdomain || "Unknown"
    },
    cross_references: Object.entries(m.cross_references || {}).map(([id, text]) => ({ req_id: id, text })),
    related_maps: (m.related_maps || []).map(rm_id => {
      const rm = mapsOutputMap.get(rm_id);
      return {
        map_id: rm_id,
        title: rm ? rm.task_title : rm_id,
        priority: rm ? rm.priority : "Medium"
      };
    })
  };
});
