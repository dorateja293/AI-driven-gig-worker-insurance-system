# Email OTP Testing Guide

## ✅ Setup Complete!

Your Gmail App Password is now configured and working:
- ✅ Environment variables loaded from `.env`
- ✅ SMTP connection to Gmail established  
- ✅ Authentication successful
- ✅ Test email sent successfully
- ✅ Backend server running on `http://localhost:5000`
- ✅ Frontend server running on `http://localhost:5174`

---

## 🧪 Full System Test (Complete OTP Flow)

### Test Case 1: Register with Email OTP

**Steps:**
1. Open http://localhost:5174/register in your browser
2. Fill in form:
   - Name: Test User
   - Email: **YOUR_EMAIL** (or insurex480@gmail.com to use the test account)
   - Reference Number: REF123456
3. Click "Send OTP" button
4. Check your email inbox for OTP code
5. Enter 6-digit OTP in the boxes
6. Click "Verify OTP"
7. Verify success message appears: "✓ Email verified successfully"

**Expected Results:**
```
Backend Logs:
  📧 Attempting to send OTP to [your-email]
  🔒 TLS connection established
  ✅ Gmail login successful
  ✅ OTP email sent successfully to [your-email]
  💾 OTP stored for [your-email], expires at [time]

Frontend:
  ✓ Loading message shows while sending
  ✓ OTP input boxes appear after success
  ✓ Success message with green checkmark
  ✓ Continue button becomes enabled
```

### Test Case 2: Login with Email OTP

**Steps:**
1. Open http://localhost:5174/login in your browser
2. Fill in form:
   - Worker ID: WORKER001
   - Email: **YOUR_EMAIL** (same as registered)
3. Click "Send OTP" button
4. Check your email for OTP code
5. Enter 6-digit OTP in the boxes
6. Click "Verify OTP"
7. Should see success message

### Test Case 3: Error Handling - Invalid OTP

**Steps:**
1. Go to http://localhost:5174/login
2. Enter Worker ID and Email
3. Click "Send OTP"
4. Receive OTP in email
5. Enter WRONG OTP (e.g., 000000)
6. Click "Verify OTP"

**Expected Result:**
```
Error message should show:
❌ Invalid OTP. Try again.

Backend logs should show:
⚠️ OTP verification failed - incorrect OTP for [email]
```

### Test Case 4: Error Handling - Expired OTP

**Steps:**
1. Go to http://localhost:5174/register
2. Enter email and click "Send OTP"
3. **Wait 5+ minutes** (OTP expires after 5 minutes)
4. Enter correct OTP in boxes
5. Click "Verify OTP"

**Expected Result:**
```
Error message should show:
❌ OTP has expired. Please request a new one.

Backend logs:
❌ OTP verification failed - OTP expired for [email]
```

### Test Case 5: Error Handling - Too Many Attempts

**Steps:**
1. Go to http://localhost:5174/register
2. Enter email and click "Send OTP"
3. Receive OTP but intentionally enter WRONG code 5 times
4. On 6th attempt, click "Verify OTP"

**Expected Result:**
```
Error message should show:
❌ Too many attempts. Please request a new OTP.

Backend logs (on 5th fail):
⚠️ OTP verification failed - 5 attempts exceeded
💾 OTP deleted due to max attempts exceeded

New OTP Sent:
User should see "Send OTP" button enabled again to retry
```

### Test Case 6: Rate Limiting - Resend OTP

**Steps:**
1. Go to http://localhost:5174/login
2. Enter Worker ID and Email
3. Click "Send OTP"
4. **Immediately** click "Send OTP" again (within 5 seconds)

**Expected Result:**
```
Second attempt message should show:
⏳ OTP already sent. Please wait X seconds before requesting again.

OR user can click "Resend OTP" button to bypass rate limit
```

---

## 📊 Backend Log Monitoring

**Terminal 1: Watch Backend Logs**

Open a terminal and watch this folder for live logs:
```bash
cd backend
tail -f flask_debug.log  # If logging to file
```

**Example Output When Sending OTP:**
```
14:36:45 [INFO] 📧 Attempting to send OTP to user@example.com
14:36:45 [INFO] 🔒 TLS connection established
14:36:45 [INFO] ✅ Gmail login successful
14:36:45 [INFO] ✅ OTP email sent successfully to user@example.com
14:36:45 [INFO] 💾 OTP stored for user@example.com, expires at 2026-04-03 14:41:45
```

**Example Output When Verifying OTP:**
```
14:36:50 [INFO] 🔐 OTP verification request for user@example.com
14:36:50 [INFO] ✅ OTP verification successful for user@example.com
14:36:50 [INFO] 💾 OTP deleted after successful verification
```

---

## 🐛 Troubleshooting

### Issue: "Connection error" on Frontend

**Cause:** Backend server not running

**Fix:**
```bash
# Check if backend is running
curl http://localhost:5000/api/health

# Restart backend
cd backend
python run.py
```

### Issue: "Gmail authentication failed" in Backend Logs

**Cause:** Wrong EMAIL_PASS in .env

**Fix:**
1. Check your App Password from Google Account
2. Make sure no spaces (should be 16 chars no spaces)
3. Update `.env`:
   ```
   EMAIL_PASS=cvrksllhszbydrsd  # No spaces!
   ```
4. Restart backend: `python run.py`

### Issue: "No OTP found for this email"

**Cause:** OTP expired or email doesn't match

**Fix:**
- Click "Send OTP" again
- Make sure email matches exactly
- Wait for email to arrive (may take 30 seconds)

### Issue: "Too many failed attempts" immediately

**Cause:** Previous OTP attempt exceeded max tries

**Fix:**
- Click "Resend OTP" button
- Or wait 5 minutes for OTP to auto-expire
- Request new OTP

### Issue: Email not arriving

**Possible causes:**
1. Check spam/junk folder
2. Check if email address is typed correctly
3. Wait 30 seconds (Gmail can be slow)
4. Check Gmail "Sent" folder - if test email arrived, SMTP works
5. Check backend logs for errors:
   ```bash
   # Look for ❌ error messages
   tail -n 50 [terminal where backend is running]
   ```

**Fix:**
- Click "Resend OTP" button
- Or request new OTP with different email

---

## ✨ Advanced Testing

### Test with Different Email Addresses

**Try Register with:**
- Your personal email: user@gmail.com
- Work email: user@company.com
- Development email: dev@example.com

**Note:** SMTP reply-to will always be `insurex480@gmail.com`, but you can customize this by updating `OTPService` in `backend/app/services/otp_service.py`

### Test API Directly with cURL

**Send OTP:**
```bash
curl -X POST http://localhost:5000/api/auth/send-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com"}'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "OTP sent to your email",
  "expiresIn": 300
}
```

**Verify OTP:**
```bash
curl -X POST http://localhost:5000/api/auth/verify-otp \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","otp":"123456"}'
```

**Expected Response (if OTP correct):**
```json
{
  "verified": true,
  "message": "OTP verification successful"
}
```

---

## 📈 Performance Metrics

| Metric | Expected Time |
|--------|----------------|
| OTP Generation | < 1ms |
| Email Send Time | 1-5 seconds |
| SMTP Connection | < 2 seconds |
| OTP Verification | < 500ms |
| Total Register Flow | < 10 seconds |

---

## ✅ Success Criteria

Your Email OTP system is **FULLY WORKING** when:

- [ ] Backend server runs without errors (`python run.py`)
- [ ] Frontend server runs without errors (`npm run dev`)
- [ ] Test email received from `insurex480@gmail.com`
- [ ] Can send OTP from Register page
- [ ] Can receive OTP in email inbox
- [ ] Can verify OTP on Register page
- [ ] Can send OTP from Login page
- [ ] Can verify OTP on Login page
- [ ] Error messages show for invalid OTP
- [ ] Error messages show for expired OTP
- [ ] Backend logs show all ✅ success messages

---

## 📝 Notes

- **OTP Validity:** 5 minutes
- **Max Attempts:** 5 wrong entries per OTP
- **Rate Limit:** 1 OTP per 5 minutes per email
- **Storage:** In-memory (resets if server restarts)
- **Production:** Use Redis or Database for persistent OTP storage

---

**Created:** April 3, 2026  
**Status:** Ready for Testing ✅
