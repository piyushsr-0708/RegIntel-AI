# Quick Verification Guide

## Start the Application

```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend  
cd frontend/dashboard
npm run dev
```

Navigate to: http://localhost:5173

---

## Task 1: Executive Dashboard Consistency

### What to Check

1. **Login as Admin**

2. **Navigate to Executive Dashboard**

3. **Check Labels:**
   - ✅ Should say "Published Assignments" (not "Published MAPs")
   - ✅ Should say "Draft Assignments" (not "Unpublished MAPs")

4. **Verify Metrics Use Published Only:**
   - Open DevTools → Network → Refresh page
   - Check `/api/admin/dashboard` response
   - All operational metrics should filter by `is_published == true`

5. **Check Upcoming Deadlines:**
   - Should only count assignments with actual due dates
   - No fallback for Critical/High without dates

---

## Task 2: Full Text Viewer

### Test 1: Department Workspace

1. **Login as Department User** (e.g., Treasury Operations)
2. Navigate to **"My Assignments"**
3. **Click on any truncated requirement text**
4. **Verify:**
   - ✅ Modal opens
   - ✅ Complete text shown (no truncation)
   - ✅ Paragraph breaks preserved
   - ✅ Metadata displayed
   - ✅ Can close by clicking backdrop, X, or Close button

---

### Test 2: Assignment Center

1. **Login as Admin**
2. Navigate to **Assignment Center**
3. **Click on any sample requirement text**
4. **Verify:**
   - ✅ Loading state appears
   - ✅ Modal opens with full text
   - ✅ Metadata displayed
   - ✅ Can close modal

---

### Test 3: Requirements Page

1. Navigate to **Requirement Search**
2. Search for **"KYC"** or **"AML"**
3. **Click "View Full Text →" button** on any requirement card
4. **Verify:**
   - ✅ Modal opens immediately
   - ✅ Full text displayed
   - ✅ Formatting preserved
   - ✅ "Trace Lifecycle" button still works independently

---

### Test 4: Knowledge Graph

1. Navigate to **Knowledge Graph**
2. **Click on a green requirement node**
3. **Verify:**
   - ✅ Node details show in right panel
   - ✅ "View Full Text →" button appears
   - ✅ Click button → modal opens with full text

4. **Click on an orange MAP node (diamond)**
5. **Verify:**
   - ✅ "View Full Text →" button appears
   - ✅ Click button → modal opens

6. **Click on a blue Circular node**
7. **Verify:**
   - ✅ NO "View Full Text" button (correct - no text content)

8. **Click on a purple Department node (hexagon)**
9. **Verify:**
   - ✅ NO "View Full Text" button (correct - no text content)

---

## Expected Results

### Task 1
- Dashboard labels updated
- All operational metrics filter by published assignments only
- Published/Draft counts remain unchanged

### Task 2
- Full text viewer works in 4 locations:
  1. Department Workspace
  2. Assignment Center
  3. Requirements Search
  4. Knowledge Graph
- No text truncation anywhere
- Original formatting preserved
- Metadata displayed correctly

---

## Quick Checklist

- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173
- [ ] Can login as admin
- [ ] Can login as department user
- [ ] Dashboard shows "Published Assignments" label
- [ ] Dashboard shows "Draft Assignments" label
- [ ] Full text modal works in Department Workspace
- [ ] Full text modal works in Assignment Center
- [ ] Full text modal works in Requirements page
- [ ] Full text modal works in Graph (requirement nodes)
- [ ] Full text modal works in Graph (MAP nodes)
- [ ] No "View Full Text" button on Circular/Department nodes
- [ ] All text displays without truncation
- [ ] Modal closes properly (backdrop, X, Close button)

---

## Troubleshooting

**Modal not opening?**
- Check browser console for errors
- Verify API endpoints are responding (DevTools → Network tab)

**Text still truncated?**
- Verify FullTextModal component is using `whiteSpace: "pre-wrap"`
- Check that correct data is passed to modal

**"View Full Text" button not appearing?**
- Verify node type is "requirement" or "map" in Graph.jsx
- Check that component state is properly initialized

**API errors?**
- Ensure backend is running
- Check that assignment/requirement IDs are valid
- Verify authentication token is valid
