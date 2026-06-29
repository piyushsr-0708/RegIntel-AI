# SINGLE SOURCE OF TRUTH AUDIT

| Page | Current Data Source | Should Read From | API Endpoint | Backend Table | Demo File | Session | Status |
|------|---------------------|------------------|--------------|---------------|-----------|---------|--------|
| **Pipeline** | session.analysis (demo-derived) | Backend API | POST /admin/process-document | requirements, assignments | maps_output.json, requirements_taxonomy.json | Yes (from demo) | 🔴 ARCHITECTURE VIOLATION |
| **Dashboard** | 3-way: session → API → demo | Backend API | GET /admin/dashboard | requirements, assignments | dashboard_metrics.json | Yes (conditional) | 🔴 ARCHITECTURE VIOLATION |
| **Assignment Center** | Backend API | Backend API | GET /assignment-center/summary | assignments | None | No | ✅ CORRECT |
| **MAP Management** | Demo (globalMapsOutput) OR session.analysis.maps | Backend API | Backend endpoint missing | assignments | maps_output.json | Yes (conditional) | 🔴 ARCHITECTURE VIOLATION |
| **Department Dashboard** | Backend API | Backend API | GET /assignment-center/department-risk | assignments | None | No | ✅ CORRECT |
| **Department Workspace** | Backend API | Backend API | GET /workspace/tasks | assignments | None | No | ✅ CORRECT |
| **Knowledge Graph** | Demo (globalGraphData) OR session.analysis.scopedGraph | Backend API | Backend endpoint missing | None | reference_graph_v2.json | Yes (conditional) | 🔴 ARCHITECTURE VIOLATION |
| **Requirements** | Demo (requirementsTaxonomy) | Backend API | GET /admin/requirements | requirements | requirements_taxonomy.json | No | 🔴 ARCHITECTURE VIOLATION |
| **MAP Detail** | Demo (mapDetails) | Backend API | Backend endpoint missing | assignments | map_details.json | No | 🔴 ARCHITECTURE VIOLATION |

---

## Summary

**✅ CORRECT:** 3 pages (33%)
- Assignment Center
- Department Dashboard  
- Department Workspace

**🔴 ARCHITECTURE VIOLATION:** 6 pages (67%)
- Pipeline (uses demo via session instead of backend response)
- Dashboard (mixes 3 sources)
- MAP Management (uses demo, no backend endpoint)
- Knowledge Graph (uses demo, no backend endpoint)
- Requirements (uses demo only, ignores backend)
- MAP Detail (uses demo, no backend endpoint)

**Critical:** 67% of pages violate Single Source of Truth principle
