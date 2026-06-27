# Frontend Authentication Testing Instructions

## Prerequisites
1. Backend must be running at http://localhost:8000
2. Test that backend is accessible:
   ```bash
   curl http://localhost:8000/api/health
   ```

## Start Frontend
```bash
cd frontend/dashboard
npm run dev
```

Frontend will be available at: http://localhost:5173

## Test Sequence

### Test 1: Initial Load (Unauthenticated)
1. Open browser to http://localhost:5173
2. Open browser console (F12)
3. Expected behavior:
   - Login page should display
   - Console should show:
     ```
     [AUTH] Checking for existing session...
     [AUTH] Token found: false
     [AUTH] User data found: false
     [AUTH] No existing session found
     [AUTH] Auth initialization complete
     [APP_ROUTES] Rendering - isAuthenticated: false loading: false
     [APP_ROUTES] Auth check complete, rendering routes
     ```

### Test 2: Admin Login
1. Enter credentials:
   - Username: `admin`
   - Password: `admin123`
2. Click "Sign In"
3. Expected console output:
   ```
   [LOGIN] Form submitted - username: admin
   [AUTH] Login attempt: admin
   [AUTH] Sending login request to: http://localhost:8000/api/auth/login
   [AUTH] Login response received: {access_token: "...", token_type: "bearer"}
   [AUTH] Storing token in localStorage
   [AUTH] Token stored: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   [AUTH] Fetching user info from: http://localhost:8000/api/auth/me
   [AUTH] User info received: {username: "admin", role: "head_office", ...}
   [AUTH] User data stored in localStorage
   [AUTH] AuthContext user state updated: {username: "admin", ...}
   [LOGIN] Login result: {success: true, user: {...}}
   [LOGIN] Login successful, user role: head_office
   [LOGIN] Redirecting to / (Head Office dashboard)
   [PROTECTED_ROUTE] Checking access - isAuthenticated: true loading: false
   [PROTECTED_ROUTE] Authenticated, allowing access
   ```
4. Expected behavior:
   - Dashboard page loads
   - User info displayed in top-right corner
   - URL is http://localhost:5173/

### Test 3: Check localStorage
1. In browser console, run:
   ```javascript
   console.log('Token:', localStorage.getItem('token'));
   console.log('User:', localStorage.getItem('user'));
   ```
2. Expected output:
   - Token should be a long JWT string
   - User should be a JSON object with username, role, etc.

### Test 4: Page Refresh (Session Persistence)
1. Press F5 or refresh the page
2. Expected console output:
   ```
   [AUTH] Checking for existing session...
   [AUTH] Token found: true
   [AUTH] User data found: true
   [AUTH] Parsed user data: {username: "admin", ...}
   [AUTH] Session restored for user: admin
   [AUTH] Auth initialization complete
   [APP_ROUTES] Rendering - isAuthenticated: true loading: false
   [APP_ROUTES] Auth check complete, rendering routes
   [PROTECTED_ROUTE] Checking access - isAuthenticated: true loading: false
   [PROTECTED_ROUTE] Authenticated, allowing access
   ```
3. Expected behavior:
   - Dashboard remains loaded
   - User still logged in
   - No redirect to login page

### Test 5: Navigate to Different Pages
1. Click "Pipeline" in navigation
2. Click "MAP Management"
3. Click "Departments"
4. Expected behavior:
   - Each page loads successfully
   - User remains authenticated
   - No redirects to login
   - Console shows: `[PROTECTED_ROUTE] Authenticated, allowing access`

### Test 6: Logout
1. Click user avatar in top-right
2. Click "Logout" button
3. Expected console output:
   ```
   [TOPBAR] Logout button clicked
   [AUTH] Logout initiated
   [AUTH] Logout complete - token and user cleared
   [TOPBAR] Navigating to /login
   [PROTECTED_ROUTE] Checking access - isAuthenticated: false loading: false
   [PROTECTED_ROUTE] Not authenticated, redirecting to /login
   ```
4. Expected behavior:
   - Redirected to login page
   - localStorage cleared (check with: `localStorage.getItem('token')` should return null)
   - URL is http://localhost:5173/login

### Test 7: Try Accessing Protected Route Without Auth
1. While logged out, try to access: http://localhost:5173/dashboard
2. Expected console output:
   ```
   [AUTH] Checking for existing session...
   [AUTH] Token found: false
   [AUTH] User data found: false
   [AUTH] No existing session found
   [AUTH] Auth initialization complete
   [PROTECTED_ROUTE] Checking access - isAuthenticated: false loading: false
   [PROTECTED_ROUTE] Not authenticated, redirecting to /login
   ```
3. Expected behavior:
   - Automatically redirected to /login
   - Cannot access dashboard without authentication

### Test 8: Department User Login
1. Enter credentials:
   - Username: `compliance`
   - Password: `compliance123`
2. Click "Sign In"
3. Expected console output:
   ```
   [AUTH] Login attempt: compliance
   [AUTH] User info received: {username: "compliance", role: "department", ...}
   [LOGIN] Login successful, user role: department
   [LOGIN] Redirecting to /departments (Department dashboard)
   ```
4. Expected behavior:
   - Redirected to /departments page (not /)
   - User info shows "Department" role
   - Department name displayed

### Test 9: Invalid Credentials
1. Logout if logged in
2. Enter credentials:
   - Username: `admin`
   - Password: `wrongpassword`
3. Click "Sign In"
4. Expected console output:
   ```
   [AUTH] Login attempt: admin
   [AUTH] Login error: ...
   [LOGIN] Login failed: ...
   ```
5. Expected behavior:
   - Error message displayed
   - Remains on login page
   - No token stored

## Common Issues and Solutions

### Issue: CORS Error
```
Access to XMLHttpRequest at 'http://localhost:8000/api/auth/login' from origin 'http://localhost:5173' has been blocked by CORS policy
```
**Solution**: Ensure backend is running and CORS is configured correctly in `backend/main.py`

### Issue: Network Error
```
[AUTH] Login error: Network Error
```
**Solution**: Ensure backend is running at http://localhost:8000

### Issue: 401 Unauthorized
```
[AUTH] Login error: Request failed with status code 401
```
**Solution**: Check credentials are correct (admin/admin123)

### Issue: Token Not Stored
**Solution**: Check browser console for errors. Ensure localStorage is enabled.

### Issue: Redirect Loop
**Solution**: Clear localStorage and refresh:
```javascript
localStorage.clear();
location.reload();
```

## Success Criteria

All tests should pass:
- [x] Login page displays on initial load
- [x] Admin login successful
- [x] Token stored in localStorage
- [x] User data stored in localStorage
- [x] Redirect to correct dashboard (role-based)
- [x] Session persists after page refresh
- [x] Navigation works while authenticated
- [x] Logout clears token and redirects
- [x] Cannot access protected routes without auth
- [x] Department users redirect to /departments
- [x] Invalid credentials rejected

## Debug Tips

### View localStorage
```javascript
console.log('Token:', localStorage.getItem('token'));
console.log('User:', JSON.parse(localStorage.getItem('user')));
```

### Clear localStorage
```javascript
localStorage.clear();
location.reload();
```

### Check Auth State
```javascript
// Run in console while on any page
console.log('Is Authenticated:', !!localStorage.getItem('token'));
```

### Test API Directly
```javascript
// Test if backend is reachable
fetch('http://localhost:8000/api/health')
  .then(r => r.json())
  .then(data => console.log('Backend health:', data));
```

### Test Login API Directly
```javascript
const formData = new FormData();
formData.append('username', 'admin');
formData.append('password', 'admin123');

fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  body: new URLSearchParams(formData)
})
  .then(r => r.json())
  .then(data => console.log('Login response:', data));
```
