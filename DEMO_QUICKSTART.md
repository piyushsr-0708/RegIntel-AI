# MVP Demo - Quick Start Guide

**For Tomorrow's University Demonstration**

---

## 🚀 Starting the Application

### 1. Start Backend (Terminal 1)

```bash
cd backend
uvicorn main:main --reload
```

**Expected Output:**
```
============================================================
REGINTEL AI - COMPLIANCE BACKEND STARTING
============================================================

✓ Creating database tables...
✓ Database seeding completed successfully

✓ Backend is ready!
✓ API Documentation: http://localhost:8000/api/docs
============================================================

INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend (Terminal 2)

```bash
cd frontend/dashboard
npm run dev
```

**Expected Output:**
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 3. Open Browser

Navigate to: **http://localhost:5173**

---

## 🎬 Demo Script (10 Minutes)

### Scene 1: Admin Workflow (3 minutes)

**1. Login as Admin**
```
Username: admin
Password: admin123
```

**2. Navigate to Pipeline**
- Click **Pipeline** in sidebar
- Upload any RBI circular PDF from `data/dataset/rbi/`
- Example: `data/dataset/rbi/kyc/KYC09062025.pdf`

**3. Watch Processing**
- Pipeline shows 9 stages
- Takes ~10-15 seconds
- Shows: Requirements extracted, Departments mapped, MAPs generated

**4. Open Assignment Center**
- After pipeline completes, click **Assignment Center** in sidebar
- Shows department distribution:
  ```
  Total: 320 MAPs
  
  Compliance        - 134 Tasks  [Publish]
  Cyber Security    - 87 Tasks   [Publish]
  Treasury          - 52 Tasks   [Publish]
  Risk Management   - 47 Tasks   [Publish]
  ```

**5. Publish to Compliance**
- Click **Publish** next to "Compliance"
- Alert: "Assignments published successfully!"
- Tasks are now visible to compliance team

**Talking Points:**
- "AI pipeline extracts requirements automatically"
- "System maps requirements to departments intelligently"
- "One-click publishing to specific departments"

---

### Scene 2: Department Workflow (3 minutes)

**6. Logout**
- Click logout in top-right corner

**7. Login as Compliance User**
```
Username: compliance
Password: compliance123
```

**8. View My Assignments**
- Sidebar shows **My Assignments** (not Pipeline/Upload)
- Dashboard shows:
  ```
  Total Tasks: 134
  Completed: 0
  Remaining: 134
  ```

**9. View Task Details**
- Scroll through task cards
- Each shows:
  - Priority badge (Critical/High/Medium/Low)
  - Domain (KYC, AML, etc.)
  - Full requirement text
  - Mark Completed button

**10. Mark Task Completed**
- Click **Mark Completed** on first task
- Status changes: ASSIGNED → COMPLETED
- Task card turns green
- Summary updates:
  ```
  Total Tasks: 134
  Completed: 1
  Remaining: 133
  ```

**Talking Points:**
- "Department users only see their assigned tasks"
- "Clean, simple interface for compliance officers"
- "One-click task completion tracking"

---

### Scene 3: Admin Dashboard (2 minutes)

**11. Logout**
- Click logout

**12. Login as Admin Again**
```
Username: admin
Password: admin123
```

**13. View Dashboard**
- Navigate to **Executive Dashboard**
- Scroll to **Department Assignment Status** table

**14. Show Real-Time Updates**
```
Department         | Assigned | Completed | Remaining | Progress
----------------------------------------------------------------
Compliance         |   134    |    1      |    133    |   0.7%
Cyber Security     |    0     |    0      |     0     |     -
Treasury           |    0     |    0      |     0     |     -
Risk Management    |    0     |    0      |     0     |     -
Operations         |    0     |    0      |     0     |     -
```

**15. Demonstrate Multiple Completions** (Optional)
- Logout → Login as compliance
- Mark 5 more tasks completed
- Logout → Login as admin
- Show updated dashboard:
  ```
  Compliance: 6 completed (4.5%)
  ```

**Talking Points:**
- "Head office sees real-time completion tracking"
- "Progress bars show department performance"
- "No manual reporting needed - fully automated"

---

### Scene 4: Knowledge Graph (2 minutes)

**16. Navigate to Knowledge Graph**
- Click **Knowledge Graph** in sidebar
- Shows network of requirements and relationships

**17. Demonstrate Search**
- Search for "KYC" or "Customer"
- Graph filters to relevant nodes
- Click nodes to see details

**Talking Points:**
- "AI builds knowledge graph automatically"
- "Shows regulatory dependencies and relationships"
- "Helps understand complex circular interconnections"

---

## ✅ Verification Checklist

Before the demo, verify:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Admin login works
- [ ] Department login works
- [ ] Upload works
- [ ] Pipeline completes successfully
- [ ] Assignment Center loads
- [ ] Publish works
- [ ] Department sees tasks after publish
- [ ] Mark completed works
- [ ] Admin dashboard updates
- [ ] No console errors in browser (F12)
- [ ] All navigation links work

---

## 🔧 Troubleshooting

### Backend won't start
```bash
# Check Python version (need 3.9+)
python --version

# Install dependencies
cd backend
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Check Node version (need 16+)
node --version

# Install dependencies
cd frontend/dashboard
npm install
```

### Database errors
```bash
# Delete and recreate
cd backend
rm data/compliance.db
# Restart backend - will auto-recreate
```

### CORS errors
- Check backend is running on port 8000
- Check frontend is running on port 5173
- Check browser console for specific error

### No tasks appear
- Make sure pipeline ran successfully
- Make sure you clicked Publish
- Check you're logged in as correct department user

---

## 🎯 Key Demo Messages

1. **"Fully Automated"** - No manual requirement extraction
2. **"Intelligent Mapping"** - AI assigns to correct departments
3. **"Offline & Secure"** - No cloud, no external APIs
4. **"Real-Time Tracking"** - Live completion monitoring
5. **"Simple UX"** - Clean, focused interface for compliance officers

---

## 📝 Default Credentials Reference

```
HEAD OFFICE:
  admin / admin123

DEPARTMENTS:
  compliance / compliance123
  risk / risk123
  cyber / cyber123
  treasury / treasury123
  operations / operations123
```

---

## 🎓 Q&A Preparation

**Q: How does AI extract requirements?**  
A: We use NLP + pattern matching + rule-based extraction. System identifies obligation markers ("shall", "must", "required").

**Q: How does department mapping work?**  
A: AI analyzes requirement text for domain keywords (KYC, AML, cyber) and maps to relevant departments.

**Q: Is this production-ready?**  
A: This is MVP for demonstration. Production would add verification workflows, evidence upload, and audit trails.

**Q: Can requirements be manually reassigned?**  
A: Not in MVP. Future phase includes manual override and AI confidence editing.

**Q: What about circular updates?**  
A: Future phase includes change detection and delta analysis when circulars are amended.

---

## 🚨 Emergency Backup Plan

If live demo fails:
1. Have screenshots/video ready
2. Walk through static mockups
3. Show code architecture instead
4. Demo knowledge graph only (most impressive visual)

---

**Demo Duration:** 10 minutes  
**Buffer:** 5 minutes for Q&A  
**Total:** 15 minutes

**Good luck! 🎉**
