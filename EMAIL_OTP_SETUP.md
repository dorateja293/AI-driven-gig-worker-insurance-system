# Real Email OTP Verification System - Setup Guide

This guide will help you set up the complete real Email OTP verification system for InsureX.

## ✅ What Has Been Implemented

### Backend (Flask)
- ✅ OTP Service (`app/services/otp_service.py`) - Handles OTP generation, storage, and verification
- ✅ Email Integration - SMTP with Gmail setup
- ✅ Three API Endpoints:
  - `POST /api/auth/send-otp` - Send OTP to email
  - `POST /api/auth/verify-otp` - Verify OTP code
  - `POST /api/auth/resend-otp` - Resend OTP (bypass rate limiting)

### Frontend (React)
- ✅ Register Page - Real OTP API integration
- ✅ Login Page - Real OTP API integration
- ✅ Both pages use the same Orange/Red Swiggy theme

---

## 🔧 Setup Instructions

### Step 1: Backend Environment Variables

1. Navigate to backend folder:
```bash
cd backend
```

2. Create `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Edit `.env` and set your Gmail credentials:
```
EMAIL_USER=insurex480@gmail.com
EMAIL_PASS=your_app_password_here
```

### Step 2: Get Gmail App Password

To use Gmail SMTP with your account:

1. Go to [Google Account Security](https://myaccount.google.com/security)
2. Enable "2-Step Verification" if not already enabled
3. Go to "App passwords" (search bar in top-right)
4. Select "Mail" and "Windows Computer" (or your device)
5. Google will generate a 16-character password
6. Copy it and paste in `.env` as `EMAIL_PASS`

**Note:** Gmail app password is different from your regular password!

### Step 3: Start Backend Server

```bash
cd backend
python run.py
```

You should see:
```
🚀 Starting InsureX Backend Server
📍 Demo endpoint: POST http://localhost:5000/api/demo/run
```

### Step 4: Start Frontend Server

In a new terminal:
```bash
cd frontend
npm run dev
```

---

## 📧 How It Works

### User Registration Flow

1. **User enters email** → Click "Send OTP"
2. **Backend:**
   - Generates 6-digit OTP
   - Sends via Gmail SMTP
   - Stores OTP with 5-minute expiry
3. **User receives email** with OTP code
4. **User enters OTP** in 6 input boxes
5. **Backend verifies** OTP matches and hasn't expired
6. **If valid:** Email marked as verified, user can continue registration
7. **If invalid:** Shows error message, user can try again (max 5 attempts)

### User Login Flow

Same as registration - requires email OTP verification

---

## 🧪 Testing Without Gmail Setup (Demo Mode)

If Gmail is not configured:

1. OTP will still be generated
2. Check **backend console logs** to see the OTP
3. Frontend will show demo message
4. Use the OTP from logs to test

Example backend log:
```
🔐 Generated OTP for user@email.com: 123456
```

---

## 🔐 API Endpoints

### 1. Send OTP
```
POST /api/auth/send-otp
Content-Type: application/json

Request:
{
  "email": "user@example.com"
}

Response (Success):
{
  "success": true,
  "message": "OTP sent successfully to your email",
  "expiresIn": 300
}

Response (Rate Limited):
Status: 429
{
  "success": false,
  "message": "OTP already sent. Please wait X seconds before requesting again.",
  "expiresIn": 45
}
```

### 2. Verify OTP
```
POST /api/auth/verify-otp
Content-Type: application/json

Request:
{
  "email": "user@example.com",
  "otp": "123456"
}

Response (Success):
{
  "verified": true,
  "message": "OTP verified successfully"
}

Response (Invalid):
{
  "verified": false,
  "message": "Invalid OTP. 4 attempts remaining."
}
```

### 3. Resend OTP
```
POST /api/auth/resend-otp
Content-Type: application/json

Request:
{
  "email": "user@example.com"
}

Response:
{
  "success": true,
  "message": "New OTP sent successfully to your email",
  "expiresIn": 300
}
```

---

## ✨ Features

### Backend Security
- ✅ 6-digit OTP generation
- ✅ 5-minute expiry (configurable in `OTP_EXPIRY_MINUTES`)
- ✅ Rate limiting (OTP expires, can't send again immediately)
- ✅ Maximum 5 failed attempts, then OTP is deleted
- ✅ OTP deleted after successful verification (one-time use)
- ✅ In-memory storage (fast, no database calls needed)

### Frontend UX
- ✅ Loading states ("Sending...", "Verifying...")
- ✅ Error messages with remaining attempts
- ✅ Success confirmation with checkmark (✓)
- ✅ 6 separate OTP input boxes
- ✅ Auto-focus to next box on digit entry
- ✅ Backspace support to delete digits
- ✅ Arrow key navigation
- ✅ Paste support (automatically fills all 6 digits)
- ✅ Disabled "Continue" button until OTP verified

---

##  Troubleshooting

### Issue: "Connection error. Please check backend is running."

**Solution:**
- Make sure backend server is running on port 5000
- Check if `python run.py` command executed successfully
- For frontend, verify CORS is setup (it is by default)

### Issue: "Failed to send OTP" or "Gmail authentication failed"

**Solution:**
- Check `.env` file has correct `EMAIL_USER` and `EMAIL_PASS`
- Verify Gmail app password is correct (16 characters)
- Check if 2-Step Verification is enabled on Gmail account
- Try creating a new app password

### Issue: OTP Not Received in Email

**Solution:**
- Check spam/junk folder
- Wait 30 seconds (Gmail may be slow)
- Try "Resend OTP" button
- Check backend logs for "Email sent successfully" message

### Issue: "OTP already sent. Please wait X seconds"

**Solution:**
- This is intentional rate limiting to prevent spam
- Wait the specified time or use "Resend OTP" button
- Rate limit resets when OTP expires (5 minutes)

---

##  Customization

### Change OTP Expiry Time
In `backend/app/services/otp_service.py`, line 18:
```python
OTP_EXPIRY_MINUTES = 5  # Change to desired minutes
```

### Change OTP Length
In `backend/app/services/otp_service.py`, function `generate_otp()`:
```python
# Change 100000, 999999 to generate different length
return str(random.randint(100000, 999999))  # This generates 6-digit
```

### Change Backend API URL (Frontend)
If backend runs on different port, update in:
- `frontend/src/pages/Login.jsx` - Line where `fetch('http://localhost:5000...'`
- `frontend/src/pages/Register.jsx` - Same URLs

---

## 📊 User Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    USER ENTERS EMAIL                         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
         ┌──────────────────────────────┐
         │   Click "Send OTP" Button    │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Backend Generates OTP       │
         │   Sends via Gmail SMTP        │
         │   Stores with 5-min expiry    │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │  User Receives OTP in Email  │
         │  Shows "OTP Sent" Message    │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   User Enters OTP in 6 Boxes │
         │   (123456)                   │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │   Click "Verify OTP" Button  │
         └──────────────┬───────────────┘
                        │
                        ▼
         ┌──────────────────────────────┐
         │  Backend Verifies OTP:       │
         │  - Check email exists        │
         │  - Check not expired         │
         │  - Check OTP matches         │
         │  - Check attempts < 5        │
         └──────────────┬───────────────┘
                        │
         ┌──────────────┴──────────────┐
         ▼                             ▼
    ✅ VALID                      ❌ INVALID
    Delete OTP         Show Error: "Invalid OTP"
    Mark Verified      Attempts remaining: 4
    Show ✓ Message     Offer Resend
    Enable Continue    Allow Retry
    Button

```

---

##  Testing Checklist

- [ ] Backend runs without errors
- [ ] Frontend connects to backend
- [ ] Can navigate to Register page
- [ ] Can enter email
- [ ] Can click "Send OTP"
- [ ] OTP appears in email (or backend logs)
- [ ] Can enter OTP in 6 boxes
- [ ] Can click "Verify OTP"
- [ ] Success message appears
- [ ] "Continue →" button becomes enabled
- [ ] Same flow works on Login page
- [ ] Invalid OTP shows error
- [ ] Rate limiting works (wait 5 min before new OTP)
- [ ] All UI matches orange/red Swiggy theme

---

##  Next Steps

1. Complete Gmail setup with app password
2. Start both backend and frontend servers
3. Test OTP flow on Register page
4. Test OTP flow on Login page
5. Verify emails are being sent
6. Test error scenarios (invalid OTP, expired, etc.)

**Happy coding! 🚀**
