# Frontend Authentication Verification Checklist

## Pre-Testing Checklist

- [ ] Backend running at http://localhost:8000
- [ ] Backend health check passes: `curl http://localhost:8000/api/health`
- [ ] Backend users seeded (admin, compliance, etc.)
- [ ] Frontend dev server ready to start
- [ ] Browser dev tools ready (F12)

---

## Test 1: Initial Load (Unauthenticated)

**Steps:**
1. Open http://localhost:5173
2. Open browser console

**Expected Results:**
- [ ] Login page displays
- [ ] Console shows: `[AUTH] Checking for existing session...`
- [ ] Console shows: `[AUTH] No existing session found`
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Test 2: Admin Login

**Steps:**
1. Enter username: `admin`
2. Enter password: `admin123`
3. Click "Sign In"
4. Watch console output

**Expected Results:**
- [ ] Console shows: `[LOGIN] Form submitted - username: admin`
- [ ] Console shows: `[AUTH] Login response received`
- [ ] Console shows: `[AUTH] Token stored`
- [ ] Console shows: `[AUTH] User info received`
- [ ] Console shows: `[LOGIN] Login successful, user role: head_office`
- [ ] Console shows: `[LOGIN] Redirecting to / (Head Office dashboard)`
- [ ] Dashboard loads
- [ ] URL is http://localhost:5173/
- [ ] User info displayed in top-right corner
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Test 3: Check localStorage

**Steps:**
1. In browser console, run:
   ```javascript
   console.log('Token:', localStorage.getItem('token'));
   console.log('User:', localStorage.getItem('user'));
   ```

**Expected Results:**
- [ ] Token is a JWT string (starts with `eyJ`)
- [ ] User is a JSON string containing username, role, etc.
- [ ] Token length > 100 characters
- [ ] User data parseable: `JSON.parse(localStorage.getItem('user'))`

**Status:** ⬜ Pass / ⬜ Fail

**Token (first 50 chars):**
```


```

**User Data:**
```


```

---

## Test 4: Page Refresh (Session Persistence)

**Steps:**
1. Press F5 or refresh the page
2. Watch console output

**Expected Results:**
- [ ] Console shows: `[AUTH] Checking for existing session...`
- [ ] Console shows: `[AUTH] Token found: true`
- [ ] Console shows: `[AUTH] User data found: true`
- [ ] Console shows: `[AUTH] Session restored for user: admin`
- [ ] Dashboard remains visible (no redirect to login)
- [ ] User info still displayed in top-right
- [ ] URL stays at http://localhost:5173/
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Test 5: Navigation

**Steps:**
1. Click "Pipeline" in navigation
2. Click "MAP Management"
3. Click "Departments"
4. Click "Dashboard" to return

**Expected Results:**
- [ ] Each page loads successfully
- [ ] No redirect to login
- [ ] User remains authenticated throughout
- [ ] Console shows: `[PROTECTED_ROUTE] Authenticated, allowing access` for each route
- [ ] URLs change correctly
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Test 6: Logout

**Steps:**
1. Click user avatar in top-right corner
2. Click "Logout" button
3. Watch console output

**Expected Results:**
- [ ] Console shows: `[TOPBAR] Logout button clicked`
- [ ] Console shows: `[AUTH] Logout initiated`
- [ ] Console shows: `[AUTH] Logout complete - token and user cleared`
- [ ] Console shows: `[TOPBAR] Navigating to /login`
- [ ] Redirected to login page
- [ ] URL is http://localhost:5173/login
- [ ] Token cleared: `localStorage.getItem('token')` returns `null`
- [ ] User cleared: `localStorage.getItem('user')` returns `null`
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Test 7: Protected Route Without Auth

**Steps:**
1. While logged out, manually navigate to: http://localhost:5173/dashboard
2. Watch console output

**Expected Results:**
- [ ] Console shows: `[AUTH] No existing session found`
- [ ] Console shows: `[PROTECTED_ROUTE] Not authenticated, redirecting to /login`
- [ ] Automatically redirected to http://localhost:5173/login
- [ ] Cannot access dashboard
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Test 8: Department User Login

**Steps:**
1. Enter username: `compliance`
2. Enter password: `compliance123`
3. Click "Sign In"
4. Watch console output

**Expected Results:**
- [ ] Console shows: `[LOGIN] Login successful, user role: department`
- [ ] Console shows: `[LOGIN] Redirecting to /departments (Department dashboard)`
- [ ] Redirected to /departments page (NOT /)
- [ ] URL is http://localhost:5173/departments
- [ ] User info shows "Department" role
- [ ] Department name displayed (if available)
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Test 9: Invalid Credentials

**Steps:**
1. Logout if logged in
2. Enter username: `admin`
3. Enter password: `wrongpassword`
4. Click "Sign In"
5. Watch console output

**Expected Results:**
- [ ] Console shows: `[AUTH] Login error`
- [ ] Error message displayed on screen
- [ ] Remains on login page
- [ ] No token stored: `localStorage.getItem('token')` returns `null`
- [ ] No user stored: `localStorage.getItem('user')` returns `null`
- [ ] Error message is user-friendly

**Status:** ⬜ Pass / ⬜ Fail

**Error Message:**
```


```

---

## Test 10: Multiple Logins

**Steps:**
1. Login as admin
2. Logout
3. Login as compliance
4. Logout
5. Login as admin again

**Expected Results:**
- [ ] Each login succeeds
- [ ] Correct role-based redirect each time
- [ ] localStorage updated correctly each time
- [ ] Each logout clears data completely
- [ ] No stale data from previous sessions
- [ ] No errors in console

**Status:** ⬜ Pass / ⬜ Fail

**Notes:**
```


```

---

## Additional Checks

### Authorization Header
**Test:**
```javascript
// After logging in, check if API calls include Authorization header
// This would require inspecting Network tab in DevTools
// Look for any API calls and check Request Headers
```

**Expected:**
- [ ] All API calls (except /login) include: `Authorization: Bearer <token>`

**Status:** ⬜ Pass / ⬜ Fail

---

### CORS Configuration
**Test:**
```javascript
// Check console for CORS errors
```

**Expected:**
- [ ] No CORS errors in console
- [ ] All API calls successful

**Status:** ⬜ Pass / ⬜ Fail

---

### API Base URL
**Test:**
```javascript
// Check console logs for API URLs
```

**Expected:**
- [ ] All API calls go to: http://localhost:8000/api/*
- [ ] No requests to wrong URL

**Status:** ⬜ Pass / ⬜ Fail

---

## Overall Test Summary

**Total Tests:** 10 core + 3 additional = 13 tests

**Results:**
- Passed: _____ / 13
- Failed: _____ / 13
- Skipped: _____ / 13

**Overall Status:** ⬜ All Pass / ⬜ Some Fail / ⬜ Major Issues

---

## Issues Found

| Test # | Issue Description | Severity | Notes |
|--------|------------------|----------|-------|
| | | | |
| | | | |
| | | | |

---

## Debug Information

### Browser
- Browser: ________________
- Version: ________________
- OS: ________________

### Backend
- Running: ⬜ Yes / ⬜ No
- URL: http://localhost:8000
- Health: ⬜ Healthy / ⬜ Error

### Frontend
- Running: ⬜ Yes / ⬜ No
- URL: http://localhost:5173
- Build: ⬜ Dev / ⬜ Prod

### Console Errors
```




```

### Network Errors
```




```

---

## Tester Information

**Tester Name:** ___________________________

**Date:** ___________________________

**Time Started:** ___________________________

**Time Completed:** ___________________________

**Total Duration:** ___________________________

---

## Sign-Off

**Frontend Authentication Testing:**

⬜ All tests passed - Ready for production  
⬜ Minor issues found - Acceptable for deployment  
⬜ Major issues found - Requires fixes before deployment

**Comments:**
```




```

**Signature:** ___________________________ **Date:** _______________

---

## Next Steps

Based on test results:

**If All Tests Pass:**
- [ ] Remove debug logging (or disable with environment variable)
- [ ] Proceed to Phase 2: Document Upload Integration
- [ ] Update deployment documentation

**If Issues Found:**
- [ ] Document all issues in detail
- [ ] Prioritize issues (critical, major, minor)
- [ ] Fix critical issues
- [ ] Re-test after fixes
- [ ] Update this checklist with results

---

**Document Version:** 1.0  
**Created:** June 26, 2026  
**Last Updated:** June 26, 2026
