import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import time
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

load_dotenv()

# In-memory OTP store
otp_store = {}

class OTPService:
    """Service for generating and managing OTPs"""
    
    EMAIL_USER = os.getenv('EMAIL_USER', 'insurex480@gmail.com')
    EMAIL_PASS = os.getenv('EMAIL_PASS', '')
    SMTP_SERVER = 'smtp.gmail.com'
    SMTP_PORT = 587
    OTP_EXPIRY_MINUTES = 5
    
    @staticmethod
    def generate_otp():
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    @staticmethod
    def send_otp_email(email, otp):
        """Send OTP to email using Gmail SMTP"""
        try:
            # Validate credentials
            if not OTPService.EMAIL_USER or not OTPService.EMAIL_PASS:
                logger.error("❌ Email credentials not configured in .env file")
                return False
            
            logger.info(f"📧 Attempting to send OTP to {email}")
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = OTPService.EMAIL_USER
            msg['To'] = email
            msg['Subject'] = "InsureX - Your OTP Code"
            
            # Email body with HTML styling
            html_body = f"""
            <html>
                <body style="font-family: Arial, sans-serif; background-color: #f5f5f5; padding: 20px;">
                    <div style="max-width: 500px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
                        <h2 style="color: #ff6b35; text-align: center;">InsureX</h2>
                        <h3 style="color: #333; text-align: center;">Email Verification</h3>
                        
                        <p style="color: #666; text-align: center; font-size: 14px; margin: 20px 0;">
                            Your one-time password (OTP) for InsureX is:
                        </p>
                        
                        <div style="background-color: #fff3e0; border: 2px dashed #ff6b35; border-radius: 5px; padding: 20px; text-align: center; margin: 30px 0;">
                            <h1 style="color: #ff6b35; letter-spacing: 5px; font-size: 32px; margin: 0;">{otp}</h1>
                        </div>
                        
                        <p style="color: #999; text-align: center; font-size: 12px;">
                            This OTP is valid for 5 minutes only.
                        </p>
                        
                        <p style="color: #999; text-align: center; font-size: 12px; margin-top: 30px;">
                            If you did not request this code, please ignore this email.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Connect to Gmail SMTP and send
            with smtplib.SMTP(OTPService.SMTP_SERVER, OTPService.SMTP_PORT) as server:
                server.starttls()
                logger.info("🔒 TLS connection established")
                
                server.login(OTPService.EMAIL_USER, OTPService.EMAIL_PASS)
                logger.info("✅ Gmail login successful")
                
                server.send_message(msg)
                logger.info(f"✅ OTP email sent successfully to {email}")
                return True
                
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Gmail authentication failed. Check EMAIL_USER and EMAIL_PASS in .env")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Error sending email: {str(e)}")
            return False
    
    @staticmethod
    def store_otp(email, otp):
        """Store OTP with expiry time"""
        expiry_time = datetime.now() + timedelta(minutes=OTPService.OTP_EXPIRY_MINUTES)
        otp_store[email] = {
            'otp': otp,
            'expires': expiry_time,
            'attempts': 0
        }
        logger.info(f"💾 OTP stored for {email}, expires at {expiry_time}")
    
    @staticmethod
    def verify_otp(email, otp):
        """Verify OTP for given email"""
        if email not in otp_store:
            logger.warning(f"❌ OTP not found for {email}")
            return False, "No OTP found for this email. Please request a new one."
        
        otp_data = otp_store[email]
        
        # Check expiry
        if datetime.now() > otp_data['expires']:
            logger.warning(f"❌ OTP expired for {email}")
            del otp_store[email]
            return False, "OTP has expired. Please request a new one."
        
        # Check maximum attempts (max 5 attempts)
        if otp_data['attempts'] >= 5:
            logger.warning(f"❌ Too many failed attempts for {email}")
            del otp_store[email]
            return False, "Too many failed attempts. Please request a new OTP."
        
        # Verify OTP
        if otp_data['otp'] == otp:
            logger.info(f"✅ OTP verified successfully for {email}")
            del otp_store[email]  # Delete after successful verification
            return True, "OTP verified successfully"
        else:
            otp_data['attempts'] += 1
            remaining = 5 - otp_data['attempts']
            logger.warning(f"❌ Invalid OTP for {email}. Attempts remaining: {remaining}")
            return False, f"Invalid OTP. {remaining} attempts remaining."
    
    @staticmethod
    def is_otp_sent(email):
        """Check if OTP was already sent to this email"""
        if email in otp_store:
            otp_data = otp_store[email]
            if datetime.now() < otp_data['expires']:
                return True
        return False
    
    @staticmethod
    def get_otp_expiry_remaining(email):
        """Get remaining time for OTP expiry"""
        if email in otp_store:
            remaining = (otp_store[email]['expires'] - datetime.now()).total_seconds()
            if remaining > 0:
                return int(remaining)
        return 0
