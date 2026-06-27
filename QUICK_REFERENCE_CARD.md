# Quick Reference Card - Print This!

**Keep this visible during testing and demo**

---

## 🚀 Start Commands

```bash
# Backend (Terminal 1)
cd backend
uvicorn main:main --reload

# Frontend (Terminal 2)
cd frontend/dashboard
npm run dev
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

---

## 🔐 Credentials

```
HEAD_OFFICE:
admin / admin123

DEPARTMENTS:
compliance / compliance123
risk / risk123
cyber / cyber123
treasury / treasury123
operations / operations123
```

---

## 🎯 Demo Flow (10 min)

```
1. Admin Login
2. Upload Circular (Pipeline)
3. Process (~15 sec)
4. Assignment Center
5. Publish to Compliance
6. Logout
7. Compliance Login
8. My Assignments
9. Mark Completed
10. Logout
11. Admin Login
12. Dashboard (see update)
```

---

## ✅ Visual Checks

**Admin Sidebar Should Show:**
- Dashboard
- Pipeline
- **Assignment Center** ← Must see!
- MAP Management
- Department Risk
- Requirement Search
- Knowledge Graph

**Department Sidebar Should Show:**
- **My Assignments** ← Must see!
- Requirement Search
- Knowledge Graph
- (NO Pipeline, NO Assignment Center)

**Topbar Should Show:**
- Logo
- Live badge
- User menu
- (NO Demo button, NO nav links)

---

## 🔍 What to Check

**Layout:**
- [ ] No horizontal scroll
- [ ] Sidebar on left
- [ ] Topbar simplified
- [ ] User menu visible

**Assignment Center (Admin):**
- [ ] In sidebar
- [ ] Shows departments
- [ ] Has counts
- [ ] Publish works

**My Assignments (Department):**
- [ ] Shows tasks
- [ ] Priority colors
- [ ] Mark Completed works
- [ ] Counts update

**Dashboard (Admin):**
- [ ] Completion table
- [ ] Real counts
- [ ] Not zeros
- [ ] Updates live

---

## 🚨 Common Issues

**Horizontal scroll?**
→ Hard refresh (Ctrl+Shift+R)

**Assignment Center empty?**
→ Run pipeline first

**Publish no effect?**
→ Check console (F12)

**Department sees admin pages?**
→ Check user role

**Mark Completed fails?**
→ Check enum usage

**Counts all zero?**
→ Check published filter

---

## 📊 Success Criteria

**MVP is ready if:**
✅ No horizontal scroll
✅ Assignment Center visible (admin)
✅ Sidebar role-based
✅ Publish creates tasks
✅ Department sees tasks
✅ Mark completed works
✅ Dashboard shows real data
✅ No console errors

---

## 💡 Demo Tips

1. **Slow down** - Let viewers see
2. **Explain** - What you're doing
3. **Highlight** - Key features
4. **Stay calm** - If errors happen
5. **Use backup** - Screenshots ready

**Key Points:**
- "Fully automated extraction"
- "Intelligent department mapping"
- "Offline and secure"
- "Real-time tracking"
- "Simple UX"

---

## 🔧 Emergency Fixes

```bash
# Restart backend
Ctrl+C
uvicorn main:main --reload

# Restart frontend
Ctrl+C
npm run dev

# Clear browser
Ctrl+Shift+Delete

# Hard refresh
Ctrl+Shift+R
```

---

## 📁 Files Changed

```
frontend/dashboard/src/App.jsx
frontend/dashboard/src/components/Topbar.jsx
backend/crud.py
backend/routers/department_workspace_router.py
```

---

## 🎬 Opening Line

"RegIntel AI is an offline compliance intelligence platform that automates RBI regulatory analysis and department task distribution."

---

## 🎤 Closing Line

"This MVP demonstrates the complete workflow from circular upload to department completion tracking, all running offline with real-time updates."

---

## 📞 If Asked

**"Can it do X?"**
→ "Great idea, planned for Phase 3"

**"What about Y?"**
→ "Current focus is core workflow"

**"Why offline?"**
→ "Security and data sovereignty"

**"How accurate?"**
→ "Uses NLP + rule-based extraction"

**"Deployment?"**
→ "SQLite for demo, PostgreSQL for production"

---

**KEEP CALM AND DEMO ON! 🚀**

---
