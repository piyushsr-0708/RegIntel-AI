import json

# Check if executive_summary is just a subset of dashboard_metrics
with open('maps/dashboard_metrics.json') as f:
    dm = json.load(f)
with open('maps/executive_summary.json') as f:
    es = json.load(f)

print('=== EXECUTIVE SUMMARY FIELDS ===')
for k,v in es.items():
    in_dm = k in dm
    match = dm.get(k) == v if in_dm else False
    print(f'  {k}: value={v}, in_dashboard_metrics={in_dm}, matches={match}')

# Check if top_risk_departments matches department_risk_scores
with open('maps/top_risk_departments.json') as f:
    trd = json.load(f)
print()
print('=== TOP RISK DEPARTMENTS vs DASHBOARD department_risk_scores ===')
for entry in trd:
    dept = entry['department']
    dm_score = dm['department_risk_scores'].get(dept, 'MISSING')
    match = dm_score == entry['risk_score']
    score = entry['risk_score']
    print(f'  {dept}: trd={score}, dm={dm_score}, match={match}')

# Check heatmap totals vs department_summary
with open('maps/department_heatmap.json') as f:
    hm = json.load(f)
with open('maps/department_summary.json') as f:
    ds = json.load(f)
print()
print('=== HEATMAP TOTALS vs DEPARTMENT_SUMMARY ===')
for dept, levels in hm.items():
    total = sum(levels.values())
    ds_count = ds.get(dept, 'MISSING')
    print(f'  {dept}: heatmap_total={total}, dept_summary={ds_count}, match={total==ds_count}')

# Check graph_ui vs reference_graph_v2
with open('maps/graph_ui.json') as f:
    gui = json.load(f)
with open('reference_graph_v2.json') as f:
    rg = json.load(f)
print()
print('=== GRAPH UI vs REFERENCE_GRAPH_V2 ===')
print(f'  graph_ui nodes: {len(gui["nodes"])}, ref_graph nodes: {len(rg["nodes"])}')
print(f'  graph_ui edges: {len(gui["edges"])}, ref_graph edges: {len(rg["edges"])}')
gui_node_ids = set(n['id'] for n in gui['nodes'])
rg_node_ids = set(n['id'] for n in rg['nodes'])
print(f'  node sets match: {gui_node_ids == rg_node_ids}')
