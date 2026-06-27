# Quick Verification Checklist

**Purpose:** Fast 5-minute verification that all integration is working

---

## 🚀 Quick Start

### 1. Start Services (2 minutes)

```bash
# Terminal 1: Backend
cd backend
uvicorn main:main --reload

# Terminal 2: Frontend
cd frontend/dashboard
npm run dev
```

**Verify:**
- Backend: http://localhost:8000/docs shows Swagger UI
- Frontend: http://localhost:5173 shows login page

---

### 2. Quick Test (3 minutes)

#### Step 1: Login (10 seconds)
- Open http://localhost:5173
- Username: `admin`
- Password: `admin123`
- Click "Sign In"

**✅ Pass:** Dashboard loads, sidebar shows "Assignment Center"

---

#### Step 2: Upload (20 seconds)
- Click "Pipeline" in sidebar
- Drop any PDF file OR click "Browse File"
- Click "Initiate Processing Pipeline"

**✅ Pass:** Progress bar shows, stages animate

---

#### Step 3: Wait for Processing (15 seconds)
- Watch console logs:
```
[PIPELINE] Starting pipeline...
[PIPELINE] File uploaded, document ID: X
[PIPELINE] Processing complete
```

**✅ Pass:** Shows "✓ ANALYSIS COMPLETE"

---

#### Step 4: Check Assignment Center (10 seconds)
- Click "Assignment Center" in sidebar
- Look for department cards

**✅ Pass:** Shows 5 departments with task counts:
- Compliance: 5
- Cyber Security: 3
- Risk Management: 2
- Treasury: 2
- Operations: 2

---

#### Step 5: Publish (10 seconds)
- Find "Compliance" card
- Click "Publish" button

**✅ Pass:** Success message, card disappears

---

#### Step 6: Department View (20 seconds)
- Click user menu → Logout
- Login: `compliance` / `compliance123`
- Click "My Assignments"

**✅ Pass:** Shows 5 tasks with "Mark Completed" buttons

---

#### Step 7: Mark Completed (10 seconds)
- Click "Mark Completed" on first task

**✅ Pass:** Button changes to "Completed ✓"

---

#### Step 8: Verify Dashboard (20 seconds)
- Logout
- Login: `admin` / `admin123`
- Navigate to "Admin Dashboard"
- Check completion table

**✅ Pass:** Compliance shows:
- Assigned: 5
- Completed: 1
- Remaining: 4

---

## ✅ Success Criteria

All 8 steps passed? **INTEGRATION WORKING! 🎉**

Any step failed? See troubleshooting below.

---

## 🐛 Quick Troubleshooting

### Assignment Center Empty
```bash
# Check database
cd backend
python -c "from database import SessionLocal; from models import Assignment; print('Assignments:', SessionLocal().query(Assignment).count())"
```

If 0:
```bash
# Manually process document
curl -X POST http://localhost:8000/api/admin/process-document/1 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Department Sees No Tasks
```bash
# Check published status
cd backend
python -c "from database import SessionLocal; from models import Assignment; db = SessionLocal(); print('Published:', db.query(Assignment).filter(Assignment.is_published == True).count())"
```

If 0:
```bash
# Manually publish
python -c "
from database import SessionLocal
from models import Assignment, Department
db = SessionLocal()
dept = db.query(Department).filter(Department.name == 'Compliance').first()
for a in db.query(Assignment).filter(Assignment.department_id == dept.id).all():
    a.is_published = True
db.commit()
print('Published')
"
```

---

### Login Fails
```bash
# Re-seed database
cd backend
python -c "
from database import SessionLocal, engine
from models import Base
from utils.seed_data import seed_all

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
seed_all(SessionLocal())
print('Database reset')
"
```

---

## 📊 Expected Console Output

### Frontend Console (Browser DevTools)

**Good:**
```
[AUTH] Login attempt: admin
[AUTH] Token stored: eyJ...
[PIPELINE] Starting pipeline for file: test.pdf
[PIPELINE] File uploaded, document ID: 1
[PIPELINE] Processing complete: {requirements_created: 14, ...}
```

**Bad:**
```
Error: Network Error
Error: Request failed with status code 401
Error: Request failed with status code 500
```

---

### Backend Terminal

**Good:**
```
INFO: 127.0.0.1 - "POST /api/auth/login HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "POST /api/admin/upload HTTP/1.1" 200 OK
INFO: 127.0.0.1 - "POST /api/admin/process-document/1 HTTP/1.1" 200 OK
```

**Bad:**
```
ERROR: Exception in ASGI application
ERROR: 'NoneType' object has no attribute 'id'
ERROR: [Errno 2] No such file or directory
```

---

## 🎯 One-Liner Status Check

```bash
cd backend && python -c "from database import SessionLocal; from models import Assignment, Requirement, Document; db = SessionLocal(); print(f'Documents: {db.query(Document).count()}, Requirements: {db.query(Requirement).count()}, Assignments: {db.query(Assignment).count()}, Published: {db.query(Assignment).filter(Assignment.is_published==True).count()}')"
```

**Expected:** `Documents: 1+, Requirements: 14+, Assignments: 14+, Published: 5+`

---

## 📝 Quick Test Results

```
Date: __________
Tester: __________

[ ] Services started (backend + frontend)
[ ] Admin login works
[ ] File upload works
[ ] Pipeline processes (15-20 seconds)
[ ] Assignment Center shows 14 tasks
[ ] Publish to Compliance works
[ ] Compliance sees 5 tasks
[ ] Mark completed works
[ ] Admin dashboard shows 1 completed

RESULT: PASS / FAIL
Notes: _______________________________
```

---

## 🎉 All Green?

If all steps passed:
- ✅ Frontend-Backend integration working
- ✅ Database persistence working
- ✅ Assignment workflow working
- ✅ Role-based access working

**You're ready to demo! 🚀**

---

**Quick Verification Complete.**
