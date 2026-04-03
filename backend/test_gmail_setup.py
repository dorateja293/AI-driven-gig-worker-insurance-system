#!/usr/bin/env python3
"""
Test script to verify Gmail OTP configuration
Run this to diagnose any email/SMTP issues before starting the Flask app
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("🔍 Gmail OTP Configuration Test")
print("=" * 60)

# Step 1: Check environment variables
print("\n📋 Step 1: Checking Environment Variables")
print("-" * 60)

EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')

if not EMAIL_USER:
    print("❌ EMAIL_USER not found in .env file")
    print("   Fix: Add 'EMAIL_USER=your-email@gmail.com' to .env")
    sys.exit(1)

if not EMAIL_PASS:
    print("❌ EMAIL_PASS not found in .env file")
    print("   Fix: Add 'EMAIL_PASS=your-app-password' to .env")
    sys.exit(1)

print(f"✅ EMAIL_USER found: {EMAIL_USER}")
print(f"✅ EMAIL_PASS found: {'*' * len(EMAIL_PASS)} ({len(EMAIL_PASS)} characters)")

# Step 2: Check password format
print("\n🔐 Step 2: Validating Password Format")
print("-" * 60)

if len(EMAIL_PASS) != 16:
    print(f"⚠️  Warning: App password should be 16 characters, got {len(EMAIL_PASS)}")
    print("   Google app passwords are typically 16 chars (4 groups of 4)")
else:
    print(f"✅ Password length correct: {len(EMAIL_PASS)} characters")

# Step 3: Test SMTP connection
print("\n🌐 Step 3: Testing SMTP Connection")
print("-" * 60)

SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

try:
    print(f"📡 Connecting to {SMTP_SERVER}:{SMTP_PORT}...")
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
    print("✅ TCP connection successful")
    
    print("🔒 Initiating TLS encryption...")
    server.starttls()
    print("✅ TLS connection established")
    
except smtplib.SMTPServerDisconnected as e:
    print(f"❌ Server disconnected: {str(e)}")
    print("   Fix: Check your internet connection or firewall settings")
    sys.exit(1)
except smtplib.SMTPException as e:
    print(f"❌ SMTP error: {str(e)}")
    print("   Fix: Check SMTP server is accessible")
    sys.exit(1)
except Exception as e:
    print(f"❌ Connection error: {str(e)}")
    print("   Fix: Check your internet connection")
    sys.exit(1)

# Step 4: Test Gmail authentication
print("\n🔐 Step 4: Testing Gmail Authentication")
print("-" * 60)

try:
    print(f"🔑 Attempting login with {EMAIL_USER}...")
    server.login(EMAIL_USER, EMAIL_PASS)
    print("✅ Gmail authentication successful!")
    
except smtplib.SMTPAuthenticationError as e:
    print(f"❌ Authentication failed!")
    print(f"   Error: {str(e)}")
    print("\n   Possible fixes:")
    print("   1. Verify EMAIL_USER is correct (example: insurex480@gmail.com)")
    print("   2. Verify EMAIL_PASS is the 16-character app password (NOT your Google password)")
    print("   3. Check you generated an App Password (not regular password)")
    print("   4. App Password should have NO SPACES - check .env file")
    print("   5. Ensure 'Less secure app access' is enabled (if using regular password)")
    server.quit()
    sys.exit(1)
except smtplib.SMTPException as e:
    print(f"❌ SMTP error during login: {str(e)}")
    server.quit()
    sys.exit(1)

# Step 5: Test sending an email
print("\n📧 Step 5: Testing Email Sending")
print("-" * 60)

try:
    # Create test message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER  # Send to self
    msg['Subject'] = "InsureX - OTP Test Email"
    
    # Simple HTML body
    html_body = """
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #ff6b35;">InsureX OTP Test</h2>
            <p>This is a test email to verify your Gmail OTP configuration works correctly.</p>
            <div style="background-color: #fff3e0; padding: 15px; border-left: 4px solid #ff6b35;">
                <p><strong>Your test OTP is: 123456</strong></p>
                <p style="font-size: 12px; color: #999;">This email confirms your SMTP setup is working.</p>
            </div>
        </body>
    </html>
    """
    
    msg.attach(MIMEText(html_body, 'html'))
    
    print(f"📮 Sending test email to {EMAIL_USER}...")
    server.send_message(msg)
    print("✅ Test email sent successfully!")
    
except Exception as e:
    print(f"❌ Error sending email: {str(e)}")
    server.quit()
    sys.exit(1)

# Close connection
server.quit()
print("✅ SMTP connection closed")

# Final summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\n✨ Your Gmail OTP system is ready to use!")
print("\nNext steps:")
print("1. Check your email inbox for the test email")
print("2. Run 'python run.py' to start the Flask server")
print("3. Test OTP on Register/Login pages")
print("\n📧 Check for test email from:", EMAIL_USER)
print("=" * 60)
