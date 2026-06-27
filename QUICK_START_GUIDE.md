# RegIntel AI - Quick Start Guide
## Authentication & Compliance Platform

---

## 🚀 Quick Start (3 Steps)

### 1. Start Backend
```bash
cd d:\SuRaksha
venv\Scripts\activate
python run_backend.py
```
✅ Backend running at: http://localhost:8000  
✅ API Docs: http://localhost:8000/api/docs

### 2. Start Frontend
```bash
cd frontend\dashboard
npm run dev
```
✅ Frontend running at: http://localhost:5173

### 3. Login
Open http://localhost:5173 in your browser

**Admin Login:**
- Username: `admin`
- Password: `admin123`

**Department Login:**
- Username: `compliance` (or risk, treasury, operations, cyber, it, finance, aml, legal)
- Password: `<username>123` (e.g., `compliance123`)

---

## 🔑 All User Credentials

| Username | Password | Role | Department |
|----------|----------|------|------------|
| admin | admin123 | Head Office | - |
| compliance | compliance123 | Department | Compliance |
| risk | risk123 | Department | Risk Management |
| treasury | treasury123 | Department | Treasury |
| operations | operations123 | Department | Operations |
| cyber | cyber123 | Department | Cyber Security |
| it | it123 | Department | IT |
| finance | finance123 | Department | Finance |
| aml | aml123 | Department | AML |
| legal | legal123 | Department | Legal |

---

## 🧪 Testing Authentication

### Automated Tests
```bash
cd d:\SuRaksha
venv\Scripts\activate
python test_backend.py
```

### Manual API Testing

**Test Login (PowerShell):**
```powershell
$body = "username=admin&password=admin123"
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/login" -Method Post -Body $body -ContentType "application/x-www-form-urlencoded"
```

**Test Get User Info:**
```powershell
$token = "<paste_token_here>"
$headers = @{"Authorization" = "Bearer $token"}
Invoke-RestMethod -Uri "http://localhost:8000/api/auth/me" -Method Get -Headers $headers
```

---

## 📚 API Endpoints

### Authentication
- `POST /api/auth/login` - Login with username/password
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

### Admin (HEAD_OFFICE only)
- `GET /api/admin/users` - List all users
- `POST /api/admin/users` - Create new user
- `GET /api/admin/departments` - List departments
- `GET /api/admin/dashboard` - Dashboard summary
- `POST /api/admin/assignments` - Assign requirement to department
- `GET /api/admin/assignments` - List all assignments
- `GET /api/admin/audit-logs` - View audit logs

### Department
- `GET /api/departments/assignments` - Get department's assignments
- `PUT /api/departments/assignments/{id}/status` - Update assignment status
- `GET /api/departments/dashboard` - Department dashboard summary

---

## 🗂️ Project Structure

```
d:\SuRaksha\
├── backend/                    # FastAPI backend
│   ├── main.py                # Main application
│   ├── auth.py                # Authentication logic
│   ├── crud.py                # Database operations
│   ├── database.py            # Database configuration
│   ├── models.py              # Database models
│   ├── schemas.py             # Pydantic schemas
│   ├── security.py            # JWT & password hashing
│   ├── routers/               # API routers
│   │   ├── auth_router.py
│   │   ├── admin_router.py
│   │   └── department_router.py
│   └── utils/                 # Utilities
│       └── seed_data.py       # Database seeding
├── frontend/dashboard/        # React frontend
│   └── src/
│       ├── pages/
│       │   ├── Login.jsx      # Login page
│       │   ├── Dashboard.jsx
│       │   └── ...
│       ├── context/
│       │   └── AuthContext.jsx # Auth state management
│       └── components/
│           ├── Topbar.jsx     # Navigation with user info
│           └── ProtectedRoute.jsx # Route protection
├── data/
│   ├── compliance.db          # SQLite database
│   ├── dataset/               # Regulatory documents
│   └── chroma_db/             # Vector database
├── run_backend.py             # Backend startup script
├── test_backend.py            # Automated tests
└── requirements.txt           # Python dependencies
```

---

## 🔐 Security Features

✅ **JWT Authentication** - Stateless token-based auth  
✅ **bcrypt Password Hashing** - No plaintext passwords  
✅ **Role-Based Access Control** - HEAD_OFFICE vs DEPARTMENT  
✅ **Protected Routes** - Frontend enforces authentication  
✅ **CORS Protection** - Only allowed origins  
✅ **Audit Logging** - All actions tracked  
✅ **Session Persistence** - Token stored securely  
✅ **8-Hour Token Expiration** - Automatic timeout  

---

## 🎯 User Roles

### HEAD_OFFICE (Admin)
**Capabilities:**
- View all departments
- Manage users
- Assign requirements to departments
- View all assignments
- Access audit logs
- Dashboard with system-wide statistics

**Landing Page:** Dashboard (/)

### DEPARTMENT
**Capabilities:**
- View assigned requirements
- Update assignment status (pending → in_progress → completed)
- Add remarks to assignments
- View department-specific dashboard
- View department statistics

**Landing Page:** Department Dashboard (/departments)

---

## 🎨 Frontend Features

### Login Page (`/login`)
- Professional banking UI
- RegIntel AI branding
- Username/password inputs
- Error messages
- Loading states
- Demo credentials display

### Navigation (Topbar)
- User avatar with initial
- User full name
- Role badge
- Department name (for dept users)
- Dropdown menu with:
  - Email
  - Role
  - Logout button

### Protected Routes
All routes require authentication:
- `/` - Dashboard
- `/pipeline` - Upload Pipeline
- `/maps` - MAP Management
- `/departments` - Department Risk
- `/requirements` - Requirements
- `/graph` - Knowledge Graph

---

## 📊 Database Schema

### Tables
1. **users** - User accounts
   - id, username, hashed_password, full_name, email
   - role (head_office/department)
   - department_id, is_active, last_login

2. **departments** - Department definitions
   - id, name, code, description

3. **documents** - Uploaded documents
   - id, filename, file_path, file_size, document_type
   - uploaded_by, uploaded_at, processed, processed_at

4. **requirements** - Compliance requirements
   - id, requirement_id, title, description, category
   - priority, document_id, extracted_at

5. **assignments** - Dept assignments
   - id, requirement_id, department_id, assigned_by
   - status, remarks, assigned_at, completed_at

6. **compliance_status_history** - Status tracking
   - id, assignment_id, old_status, new_status
   - changed_by, changed_at, remarks

7. **audit_logs** - Action audit trail
   - id, user_id, action, entity_type, entity_id
   - details, ip_address, timestamp

---

## 🛠️ Troubleshooting

### Backend Won't Start
```bash
# Check if virtual environment is activated
venv\Scripts\activate

# Check if dependencies are installed
pip install -r requirements.txt

# Check if port 8000 is available
netstat -ano | findstr :8000
```

### Frontend Won't Start
```bash
# Install dependencies
cd frontend\dashboard
npm install

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check if port 5173 is available
netstat -ano | findstr :5173
```

### Login Not Working
1. Verify backend is running (http://localhost:8000/api/health)
2. Check browser console for errors
3. Verify credentials (admin/admin123)
4. Check CORS settings in backend/main.py
5. Clear browser localStorage and try again

### Token Expired
- Tokens expire after 8 hours
- Simply logout and login again
- Or clear localStorage: `localStorage.clear()`

---

## 📝 Development Notes

### Adding New Users
1. Use admin account
2. Go to http://localhost:8000/api/docs
3. Use POST /api/admin/users endpoint
4. Provide username, password, email, role, department_id

### Changing Passwords
1. Login as the user
2. Use POST /api/auth/change-password endpoint
3. Provide old_password and new_password

### Testing API with Swagger
1. Go to http://localhost:8000/api/docs
2. Click "Authorize" button
3. Login to get token
4. Paste token in authorization dialog
5. All endpoints now include the token

---

## 🚦 System Status Check

### Quick Health Check
```bash
# Backend health
curl http://localhost:8000/api/health

# Frontend (should return HTML)
curl http://localhost:5173

# Database check
python -c "from backend.database import engine; print(engine.table_names())"
```

### Run All Tests
```bash
cd d:\SuRaksha
venv\Scripts\activate
python test_backend.py
```

Expected output:
```
✓ Health check passed
✓ Login successful
✓ Get current user successful
✓ Correctly rejected invalid credentials
✓ Department login successful
✓ Swagger docs accessible
```

---

## 📞 Support

### Documentation Files
- `AUTH_FIX_REPORT.md` - Complete authentication documentation
- `PHASE1.1_COMPLETE.txt` - Phase 1.1 completion summary
- `AUTH_INTEGRATION_REPORT.md` - Frontend integration details
- `PHASE1_COMPLETE.txt` - Phase 1 implementation summary

### Log Files
- Backend logs: Console output (stdout)
- Database: `data/compliance.db`
- Frontend logs: Browser console

---

## ✅ Verification Checklist

Before reporting issues, verify:

- [ ] Virtual environment activated
- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:5173)
- [ ] Database file exists (data/compliance.db)
- [ ] No errors in backend console
- [ ] No errors in browser console
- [ ] CORS configured correctly
- [ ] Credentials typed correctly
- [ ] Token not expired (< 8 hours)

---

**Last Updated**: June 26, 2026  
**Version**: 1.0.0  
**Phase**: 1.1 Complete
