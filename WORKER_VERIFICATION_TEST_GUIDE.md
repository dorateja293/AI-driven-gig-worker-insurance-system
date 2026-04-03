# Worker Verification Test Guide

## Overview

This guide walks you through testing the realistic worker verification system with database matching.

---

## Test Environment Setup

### Prerequisites
- Flask backend running on `http://localhost:5000`
- React frontend running on `http://localhost:5173`
- Both servers should be running

### Starting the Servers

**Terminal 1 - Backend:**
```bash
cd backend
python run.py
# Output: Flask running on http://localhost:5000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
# Output: VITE ready on http://localhost:5173
```

---

## Test Scenario 1: ✅ Successful Verification

### Objective
User with correct Worker ID and matching email successfully verifies.

### Steps

1. **Open Registration Page**
   - Navigate to: `http://localhost:5173/register`

2. **Fill Personal Information**
   ```
   Full Name:  John Worker
   Email:      worker1@gmail.com  ← IMPORTANT: Must match database
   Phone:      9876543210
   City:       Mumbai
   Platform:   Swiggy
   ```

3. **Verify Email with OTP**
   - Click "Send OTP" button
   - Wait 1 second
   - Copy any 6 digits (e.g., 123456)
   - Paste into OTP boxes
   - Click "Verify OTP"
   - Wait 1 second
   - See: ✅ "Email verified successfully"

4. **Verify Worker**
   - Worker ID field: `SWG12345`
   - Email should still be: `worker1@gmail.com`
   - Click "Verify" button
   - Wait 1.5 seconds (simulating database lookup)

5. **Expected Result**
   ```
   ✅ Button shows: "✓ Verified" (green color)
   ✅ Green message box: "Verified Worker ✓"
   ✅ Info badge updates: "Your worker identity has been verified"
   ✅ Submit button: ENABLED (blue, active)
   ```

6. **Verify in Backend Logs**
   ```
   ✅ Worker verified: SWG12345 (worker1@gmail.com) - Swiggy
   ```

### Browser Console Check
```javascript
// Network tab should show:
// POST /api/auth/verify-worker → 200 OK
// Response: {
//   "verified": true,
//   "status": "verified",
//   "workerId": "SWG12345",
//   "worker_name": "John Doe",
//   "platform": "Swiggy"
// }
```

---

## Test Scenario 2: ❌ Email Mismatch

### Objective
User has correct Worker ID but provides different email than database record.

### Steps

1. **Fill Form**
   ```
   Full Name:  Test User
   Email:      wrong@gmail.com  ← WRONG EMAIL
   Phone:      9876543210
   City:       Mumbai
   Platform:   Swiggy
   ```

2. **Complete Email OTP Verification**
   - Same process as Scenario 1

3. **Verify Worker with Mismatched Email**
   - Worker ID field: `SWG12345`  ← Correct ID
   - Email field: `wrong@gmail.com`  ← Wrong email
   - Click "Verify" button
   - Wait 1.5 seconds

4. **Expected Result**
   ```
   ⚠️ Button shows: "Verify" (blue, re-enabled)
   ⚠️ Red message box: "Email does not match the worker record.
                        Please verify your email address."
   ⚠️ Submit button: DISABLED (gray, inactive)
   ```

5. **Verify in Backend Logs**
   ```
   ⚠️ Email mismatch for Worker ID SWG12345: 
      Expected worker1@gmail.com, Got wrong@gmail.com
   ```

### Browser Console Check
```javascript
// POST /api/auth/verify-worker → 400 Bad Request
// Response: {
//   "verified": false,
//   "status": "email_mismatch",
//   "message": "Worker ID exists but email does not match our records"
// }
```

---

## Test Scenario 3: ❌ Worker Not Found

### Objective
User provides a Worker ID that doesn't exist in the database.

### Steps

1. **Fill Form**
   ```
   Full Name:  Test User
   Email:      any@gmail.com
   Phone:      9876543210
   City:       Mumbai
   Platform:   Swiggy
   ```

2. **Complete Email OTP Verification**
   - Same process as Scenario 1

3. **Verify Worker with Non-existent ID**
   - Worker ID field: `SWG99999`  ← Non-existent
   - Email field: `any@gmail.com`
   - Click "Verify" button
   - Wait 1.5 seconds

4. **Expected Result**
   ```
   ⚠️ Button shows: "Verify" (blue, re-enabled)
   ⚠️ Red message box: "Worker ID not found in our system.
                        Please contact support."
   ⚠️ Submit button: DISABLED (gray, inactive)
   ```

5. **Verify in Backend Logs**
   ```
   ⚠️ Worker ID not found: SWG99999
   ```

### Browser Console Check
```javascript
// POST /api/auth/verify-worker → 404 Not Found
// Response: {
//   "verified": false,
//   "status": "not_found",
//   "message": "Worker ID SWG99999 not found in system"
// }
```

---

## Test Scenario 4: ❌ Missing Email Field

### Objective
User leaves email field empty when verifying worker.

### Steps

1. **Fill Form**
   ```
   Full Name:  Test User
   Email:      [leave empty or clear it]
   Phone:      9876543210
   City:       Mumbai
   Platform:   Swiggy
   ```

2. **Try to Verify Worker**
   - Worker ID field: `SWG12345`
   - Click "Verify" button

3. **Expected Result**
   ```
   ⚠️ No API call made (immediate validation)
   ⚠️ Can't fill Worker ID without Email field
   ⚠️ Form validation fails before verification
   ```

---

## Test All Database Workers

### Swiggy Workers ✅

**Worker 1 - John Doe**
```
Worker ID: SWG12345
Email:     worker1@gmail.com
Result:    ✅ Verified
```

**Worker 2 - Raj Kumar**
```
Worker ID: SWG67890
Email:     raj@gmail.com
Result:    ✅ Verified
```

**Worker 3 - Deepika Singh**
```
Worker ID: SWG11111
Email:     deepika@gmail.com
Result:    ✅ Verified
```

### Zomato Workers ✅

**Worker 1 - Jane Smith**
```
Worker ID: ZMT56789
Email:     worker2@gmail.com
Result:    ✅ Verified
```

**Worker 2 - Priya Sharma**
```
Worker ID: ZMT98765
Email:     priya@gmail.com
Result:    ✅ Verified
```

**Worker 3 - Alex Johnson**
```
Worker ID: ZMT44444
Email:     alex@gmail.com
Result:    ✅ Verified
```

---

## cURL Testing

### Test 1: Successful Verification
```bash
curl -X POST http://localhost:5000/api/auth/verify-worker \
  -H "Content-Type: application/json" \
  -d '{
    "workerId": "SWG12345",
    "email": "worker1@gmail.com"
  }'

# Expected: HTTP 200
# Response: {"verified": true, "status": "verified", ...}
```

### Test 2: Email Mismatch
```bash
curl -X POST http://localhost:5000/api/auth/verify-worker \
  -H "Content-Type: application/json" \
  -d '{
    "workerId": "SWG12345",
    "email": "wrong@gmail.com"
  }'

# Expected: HTTP 400
# Response: {"verified": false, "status": "email_mismatch"}
```

### Test 3: Worker Not Found
```bash
curl -X POST http://localhost:5000/api/auth/verify-worker \
  -H "Content-Type: application/json" \
  -d '{
    "workerId": "SWG99999",
    "email": "any@gmail.com"
  }'

# Expected: HTTP 404
# Response: {"verified": false, "status": "not_found"}
```

### Test 4: Missing Fields
```bash
curl -X POST http://localhost:5000/api/auth/verify-worker \
  -H "Content-Type: application/json" \
  -d '{
    "workerId": "SWG12345"
  }'

# Expected: HTTP 400
# Response: {"verified": false, "status": "invalid", 
#            "message": "Worker ID and email are both required"}
```

### Test 5: Invalid Email Format
```bash
curl -X POST http://localhost:5000/api/auth/verify-worker \
  -H "Content-Type: application/json" \
  -d '{
    "workerId": "SWG12345",
    "email": "invalidemail"
  }'

# Expected: HTTP 400
# Response: {"verified": false, "status": "invalid", 
#            "message": "Invalid email format"}
```

---

## Browser DevTools Testing

### Step 1: Open Network Tab
1. Open browser DevTools (F12 or Ctrl+Shift+I)
2. Go to "Network" tab
3. Clear previous requests

### Step 2: Run Verification
1. Fill out registration form
2. Click "Verify" button in Worker Verification section

### Step 3: Inspect Request
1. Look for `verify-worker` POST request
2. Click on it
3. Check "Request" tab:
   ```json
   {
     "workerId": "SWG12345",
     "email": "worker1@gmail.com"
   }
   ```

### Step 4: Inspect Response
1. Click "Response" tab
2. For success:
   ```json
   {
     "verified": true,
     "status": "verified",
     "message": "Worker SWG12345 verified successfully",
     "workerId": "SWG12345",
     "worker_name": "John Doe",
     "platform": "Swiggy",
     "email": "worker1@gmail.com"
   }
   ```

### Step 5: Check Status Code
1. Click on the request
2. Check "Headers" section
3. Look for "Status Code: 200" (success) or "400/404" (failure)

---

## Performance Testing

### Verification Delay Check

Expected behavior:
- Click "Verify" button
- Wait exactly 1.5 seconds
- Button text changes to "✓ Verified" or reverts to "Verify"

**What this means:**
- 1.5 second delay simulates real database query
- Production will have real database query time (~100ms)
- Prevents brute force attacks by making verification slower

### Timing Test Steps

1. Click "Verify" button
2. Start timer (use phone stopwatch)
3. Count seconds until response
4. Should be approximately 1.5 seconds

---

## Edge Cases to Test

| Edge Case | Steps | Expected |
|-----------|-------|----------|
| **Lowercase Worker ID** | Use `swg12345` instead of `SWG12345` | ✅ Should work (converted to uppercase) |
| **Lowercase Email** | Use `WORKER1@GMAIL.COM` instead of `worker1@gmail.com` | ✅ Should work (converted to lowercase) |
| **Extra Spaces** | Use ` SWG12345 ` with spaces | ✅ Should work (trimmed) |
| **Rapid Clicks** | Click Verify button 5 times quickly | ✅ Only one request (button disabled during verification) |
| **Network Offline** | Disconnect internet, click Verify | ❌ "Connection error" message |

---

## Debugging Tips

### If Verification Always Fails

**Check 1: Email Match**
```
Is the email you entered exactly matching the database?
- Case doesn't matter (both converted to lowercase)
- Spaces don't matter (both trimmed)
- But spelling must be exact
```

**Check 2: Worker ID Format**
```
Does Worker ID match exactly (case-insensitive)?
- SWG12345 ✅
- SWG67890 ✅
- ZMT56789 ✅
- All others ❌
```

**Check 3: Backend Logs**
```
Watch terminal running "python run.py"
Look for:
✅ "Worker verified: ..."  (success)
⚠️  "Email mismatch for ..." (mismatch)
⚠️  "Worker ID not found: ..." (not found)
```

### If Button Stays Disabled

Check 1: Is all other form data valid?
- Full Name ✅
- Email ✅
- Phone (10 digits) ✅
- City ✅

Check 2: Is Email OTP verified?
- Should see: ✅ "Email verified successfully"

Check 3: Is Worker verified?
- Should see: ✅ "Verified Worker ✓"

---

## Success Checklist

- [ ] Test Scenario 1: Successful verification ✅
- [ ] Test Scenario 2: Email mismatch ❌
- [ ] Test Scenario 3: Worker not found ❌
- [ ] All 6 database workers can be verified ✅
- [ ] cURL tests all work as expected ✅
- [ ] Backend logs show correct messages ✅
- [ ] Network tab shows correct HTTP status codes ✅
- [ ] Error messages are clear and helpful ✅
- [ ] Button states change correctly ✅
- [ ] Submit button only enabled when all conditions met ✅

---

## Summary

The realistic worker verification system is working correctly when:

✅ Users can verify with correct Worker ID and email
✅ System rejects mismatched emails with clear error
✅ System rejects non-existent worker IDs with clear error
✅ All 6 mock database workers can be verified
✅ 1.5 second delay simulates real database lookup
✅ Clear error messages help users understand what went wrong
✅ Form submission only enabled when fully verified
