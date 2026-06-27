# MVP Demo Workflow - Visual Diagrams

**Visual representation of the complete workflow**

---

## 🔄 Complete System Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    HEAD OFFICE (ADMIN)                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ Login
                            ↓
                   ┌─────────────────┐
                   │   Dashboard     │
                   └─────────────────┘
                            │
                            │ Navigate to Pipeline
                            ↓
                   ┌─────────────────┐
                   │  Upload RBI     │
                   │   Circular      │
                   └─────────────────┘
                            │
                            │ Process
                            ↓
                   ┌─────────────────┐
                   │  AI Pipeline    │
                   │  (9 Stages)     │
                   └─────────────────┘
                            │
                            │ Extract & Classify
                            ↓
      ┌─────────────────────┴─────────────────────┐
      │                                            │
      ↓                                            ↓
┌──────────┐                                ┌──────────┐
│ 134 Reqs │                                │ 87 Reqs  │
│COMPLIANCE│                                │  CYBER   │
└──────────┘                                └──────────┘
      │                                            │
      │                                            │
      │         Navigate to Assignment Center     │
      │                    ↓                       │
      │         ┌─────────────────────┐           │
      │         │ View Distribution   │           │
      │         │                     │           │
      │         │ Compliance: 134     │           │
      │         │ Cyber Sec:  87      │           │
      │         │ Treasury:   52      │           │
      │         └─────────────────────┘           │
      │                    │                       │
      │         Click "Publish" on Compliance     │
      │                    ↓                       │
      │         ┌─────────────────────┐           │
      │         │  is_published =     │           │
      │         │       TRUE          │           │
      │         └─────────────────────┘           │
      │                    │                       │
      └────────────────────┼───────────────────────┘
                           │
                           │ Tasks now visible
                           ↓
┌─────────────────────────────────────────────────────────────┐
│               DEPARTMENT (COMPLIANCE)                        │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Login
                           ↓
                  ┌─────────────────┐
                  │ My Assignments  │
                  │                 │
                  │ Total: 134      │
                  │ Completed: 0    │
                  │ Remaining: 134  │
                  └─────────────────┘
                           │
                           │ View Tasks
                           ↓
              ┌────────────────────────┐
              │ Task 1: [CRITICAL]     │
              │ KYC requirement...     │
              │ [Mark Completed] ←─────┼── Click
              └────────────────────────┘
                           │
                           │ Update Status
                           ↓
              ┌────────────────────────┐
              │ status = COMPLETED     │
              │ completed_at = NOW     │
              └────────────────────────┘
                           │
                           │ Propagate
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                HEAD OFFICE (ADMIN) - Dashboard               │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ Real-time Update
                           ↓
        ┌──────────────────────────────────────┐
        │ Department Assignment Status         │
        ├──────────────────────────────────────┤
        │ Dept      │ Assigned │ Completed │ % │
        ├───────────┼──────────┼───────────┼───┤
        │ Compliance│   134    │     1     │1% │
        │ Cyber Sec │    0     │     0     │ - │
        └──────────────────────────────────────┘
```

---

## 🎯 User Journey Maps

### Journey 1: Admin Publishes Assignments

```
Step 1: LOGIN
┌────────────────┐
│  Login Screen  │
│                │
│ [Username]     │
│ [Password]     │
│   [Login]      │
└────────────────┘
        ↓
   admin/admin123
        ↓

Step 2: UPLOAD & PROCESS
┌────────────────┐
│   Pipeline     │
│                │
│ [Drag PDF]     │
│                │
│ [Process] ─────┼─→ 9 Stages → Results
└────────────────┘
        ↓
   RBI_Circular.pdf
        ↓

Step 3: REVIEW ASSIGNMENTS
┌────────────────────────┐
│  Assignment Center     │
│                        │
│  Total: 320 MAPs       │
│                        │
│  ┌──────────────────┐  │
│  │ Compliance: 134  │  │
│  │   [Publish]      │  │ ←── Click this
│  └──────────────────┘  │
│                        │
│  ┌──────────────────┐  │
│  │ Cyber Sec: 87    │  │
│  │   [Publish]      │  │
│  └──────────────────┘  │
└────────────────────────┘
        ↓
   ✓ Published to Compliance
```

---

### Journey 2: Department Completes Tasks

```
Step 1: LOGIN (Different User)
┌────────────────┐
│  Login Screen  │
│                │
│ [Username]     │
│ [Password]     │
│   [Login]      │
└────────────────┘
        ↓
   compliance/compliance123
        ↓

Step 2: VIEW MY TASKS
┌─────────────────────────────┐
│   My Assignments            │
│                             │
│   ┌─────┬──────┬─────────┐  │
│   │ 134 │  0   │   134   │  │
│   │Total│Compl.│Remaining│  │
│   └─────┴──────┴─────────┘  │
│                             │
│   ┌───────────────────────┐ │
│   │[CRITICAL] KYC         │ │
│   │All banks must...      │ │
│   │ [Mark Completed]      │ │ ←── Click
│   └───────────────────────┘ │
│                             │
│   ┌───────────────────────┐ │
│   │[HIGH] AML             │ │
│   │Suspicious trans...    │ │
│   │ [Mark Completed]      │ │
│   └───────────────────────┘ │
└─────────────────────────────┘
        ↓
   ✓ Task 1 Completed
   ✓ Counter: 134 → 133 remaining
```

---

### Journey 3: Admin Monitors Progress

```
Step 1: LOGIN (Back to Admin)
┌────────────────┐
│  Login Screen  │
└────────────────┘
        ↓
   admin/admin123
        ↓

Step 2: VIEW DASHBOARD
┌──────────────────────────────────────────┐
│   Executive Dashboard                    │
│                                          │
│   [KPI Cards...]                         │
│   [Charts...]                            │
│                                          │
│   ┌────────────────────────────────────┐ │
│   │ Department Assignment Status       │ │
│   ├────────────────────────────────────┤ │
│   │ Department │Assigned│Compl│Remain │ │
│   ├────────────┼────────┼─────┼───────┤ │
│   │ Compliance │  134   │  1  │  133  │ │ ←── Updated!
│   │ Cyber Sec  │   0    │  0  │   0   │ │
│   │ Treasury   │   0    │  0  │   0   │ │
│   └────────────────────────────────────┘ │
└──────────────────────────────────────────┘
```

---

## 🗺️ Page Navigation Map

### Admin Navigation

```
                    ┌─────────────┐
                    │   Login     │
                    └──────┬──────┘
                           │
                           ↓
                    ┌─────────────┐
                    │  Dashboard  │ ←────────┐
                    └──────┬──────┘          │
                           │                 │
         ┌─────────────────┼─────────────────┼──────────────┐
         │                 │                 │              │
         ↓                 ↓                 ↓              ↓
    ┌─────────┐      ┌──────────┐     ┌──────────┐   ┌────────┐
    │Pipeline │      │Assignment│     │   MAPs   │   │ Graph  │
    │         │      │ Center   │     │          │   │        │
    └─────────┘      └──────────┘     └──────────┘   └────────┘
         │                 │
         │                 │
         ↓                 ↓
    ┌─────────┐      ┌──────────┐
    │ Upload  │      │ Publish  │
    │ Process │      │  Tasks   │
    └─────────┘      └──────────┘
```

---

### Department Navigation

```
                    ┌─────────────┐
                    │   Login     │
                    └──────┬──────┘
                           │
                           ↓
                    ┌─────────────┐
                    │     My      │ ←────────┐
                    │ Assignments │          │
                    └──────┬──────┘          │
                           │                 │
         ┌─────────────────┴─────────────────┘
         │                 │
         ↓                 ↓
    ┌─────────┐      ┌──────────┐
    │  Graph  │      │  Search  │
    │         │      │          │
    └─────────┘      └──────────┘

    (NO ACCESS TO:)
    ✗ Pipeline
    ✗ Upload
    ✗ Assignment Center
    ✗ Dashboard
```

---

## 🔄 Data Flow Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        DATA FLOW                              │
└──────────────────────────────────────────────────────────────┘

1. UPLOAD
   ┌─────┐
   │ PDF │─────→ FastAPI Backend
   └─────┘           │
                     ↓
                 Store File
                     │
                     ↓
                 ┌─────────┐
                 │Document │
                 │  Table  │
                 └─────────┘

2. PROCESS
   ┌─────────┐
   │Document │─────→ AI Pipeline
   └─────────┘           │
                         ↓
                    Extract Text
                         │
                         ↓
                    Classify
                         │
                         ↓
                 ┌──────────────┐
                 │ Requirements │
                 │    Table     │
                 └──────────────┘

3. ASSIGN
   ┌──────────────┐
   │ Requirements │─────→ Department Mapper
   └──────────────┘           │
                              ↓
                          Group by Dept
                              │
                              ↓
                     ┌──────────────────┐
                     │   Assignments    │
                     │  is_published=F  │
                     └──────────────────┘

4. PUBLISH
   Admin Action ─────→ Update Query
                            │
                            ↓
                     ┌──────────────────┐
                     │   Assignments    │
                     │  is_published=T  │ ←── Now visible!
                     └──────────────────┘

5. VIEW (Department)
   ┌──────────────────┐
   │   Assignments    │
   │  is_published=T  │─────→ Filter by dept_id
   │  dept_id=1       │            │
   └──────────────────┘            ↓
                              React Component
                                   │
                                   ↓
                              Display Tasks

6. COMPLETE
   User Action ─────→ Update Query
                           │
                           ↓
                   ┌──────────────────┐
                   │   Assignments    │
                   │ status=COMPLETED │
                   │ completed_at=NOW │
                   └──────────────────┘
                           │
                           ↓
                   Propagate to Dashboard
                           │
                           ↓
                   Admin sees update
```

---

## 📊 State Diagram

```
┌─────────────────────────────────────────────────────────────┐
│              ASSIGNMENT LIFECYCLE                            │
└─────────────────────────────────────────────────────────────┘

    ┌─────────┐
    │ CREATED │  (After pipeline processing)
    └────┬────┘
         │
         │ is_published = FALSE
         │ status = PENDING
         ↓
  ┌────────────┐
  │UNPUBLISHED │  (Waiting for admin review)
  └──────┬─────┘
         │
         │ Admin clicks "Publish"
         │ is_published = TRUE
         ↓
   ┌───────────┐
   │ PUBLISHED │  (Visible to department)
   └─────┬─────┘
         │
         │ Department user clicks "Mark Completed"
         │ status = COMPLETED
         │ completed_at = NOW
         ↓
   ┌───────────┐
   │ COMPLETED │  (Shows in admin dashboard)
   └───────────┘


State Transitions:
─────────────────
CREATED → UNPUBLISHED  (Automatic)
UNPUBLISHED → PUBLISHED  (Admin action)
PUBLISHED → COMPLETED  (Department action)

Access Rules:
─────────────
UNPUBLISHED: Only HEAD_OFFICE sees (in Assignment Center)
PUBLISHED: Department users see (in My Assignments)
COMPLETED: Both see, different views
```

---

## 🏗️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (React)                         │
│                   http://localhost:5173                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ HTTP REST API
                            │ JWT Authentication
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI)                          │
│                  http://localhost:8000                       │
│                                                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │Auth Router  │  │Assignment    │  │Department    │       │
│  │             │  │Center Router │  │Workspace     │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│                                                               │
│  ┌──────────────────────────────────────────────────┐       │
│  │                  CRUD Layer                       │       │
│  │  - get_unpublished_assignment_summary()          │       │
│  │  - publish_department_assignments()              │       │
│  │  - get_published_assignments_for_department()    │       │
│  │  - mark_assignment_completed()                   │       │
│  │  - get_admin_completion_summary()                │       │
│  └──────────────────────────────────────────────────┘       │
│                            │                                 │
│                            ↓                                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │              ORM Models (SQLAlchemy)             │       │
│  │  - User                                          │       │
│  │  - Department                                    │       │
│  │  - Assignment (+ is_published column)           │       │
│  │  - Requirement                                   │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────┐
│                 DATABASE (SQLite)                            │
│              backend/data/compliance.db                      │
│                                                               │
│  ┌─────────┐  ┌───────────┐  ┌──────────────┐              │
│  │ users   │  │departments│  │ assignments  │              │
│  │         │  │           │  │ +is_published│              │
│  └─────────┘  └───────────┘  └──────────────┘              │
│                                                               │
│  ┌──────────────┐  ┌──────────┐                             │
│  │ requirements │  │documents │                             │
│  └──────────────┘  └──────────┘                             │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎬 Demo Sequence Diagram

```
Admin          Frontend        Backend         Database
  │                │              │               │
  │  Login         │              │               │
  ├────────────────>              │               │
  │                ├─POST /login──>               │
  │                │              ├─ Verify ──────>
  │                │              <── JWT ─────────┤
  │  <── Token ────┤              │               │
  │                │              │               │
  │  Upload PDF    │              │               │
  ├────────────────>              │               │
  │                ├─POST /upload─>               │
  │                │              ├─ Store ────────>
  │                │              <── Success ─────┤
  │                │              │               │
  │                │  [Pipeline processes...]     │
  │                │              │               │
  │  View Assign   │              │               │
  │  Center        │              │               │
  ├────────────────>              │               │
  │                ├─GET /summary─>               │
  │                │              ├─ Query ────────>
  │                │              <── Depts ───────┤
  │  <── Show ─────┤              │               │
  │                │              │               │
  │  Publish       │              │               │
  ├────────────────>              │               │
  │                ├─POST /publish>               │
  │                │              ├─ UPDATE ───────>
  │                │              │   is_published=T
  │                │              <── Done ────────┤
  │  <── Success ──┤              │               │
  │                │              │               │
  
Compliance     Frontend        Backend         Database
  │                │              │               │
  │  Login         │              │               │
  ├────────────────>              │               │
  │                ├─POST /login──>               │
  │                │              ├─ Verify ──────>
  │  <── Token ────┤              │               │
  │                │              │               │
  │  View Tasks    │              │               │
  ├────────────────>              │               │
  │                ├─GET /my-tasks>               │
  │                │              ├─ SELECT ──────>
  │                │              │   WHERE dept_id=1
  │                │              │   AND is_published=T
  │                │              <── Tasks ───────┤
  │  <── Display ──┤              │               │
  │                │              │               │
  │  Mark Complete │              │               │
  ├────────────────>              │               │
  │                ├─POST /complete               │
  │                │              ├─ UPDATE ───────>
  │                │              │   status=COMPLETED
  │                │              <── Done ────────┤
  │  <── Success ──┤              │               │
```

---

**Use these diagrams during the demo to explain the workflow visually!** 📊

---
