from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Wallet
from app.utils import generate_token
from app.services.otp_service import OTPService
import logging
import time
import requests
import os

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

# Mock database of valid workers
# In production, this would be a real database table
VALID_WORKERS = [
    {
        "workerId": "SWG12345",
        "email": "worker1@gmail.com",
        "platform": "Swiggy",
        "name": "John Doe"
    },
    {
        "workerId": "SWG67890",
        "email": "raj@gmail.com",
        "platform": "Swiggy",
        "name": "Raj Kumar"
    },
    {
        "workerId": "SWG11111",
        "email": "deepika@gmail.com",
        "platform": "Swiggy",
        "name": "Deepika Singh"
    },
    {
        "workerId": "ZMT56789",
        "email": "worker2@gmail.com",
        "platform": "Zomato",
        "name": "Jane Smith"
    },
    {
        "workerId": "ZMT98765",
        "email": "priya@gmail.com",
        "platform": "Zomato",
        "name": "Priya Sharma"
    },
    {
        "workerId": "ZMT44444",
        "email": "alex@gmail.com",
        "platform": "Zomato",
        "name": "Alex Johnson"
    },
    {
        "workerId": "SWG2007",
        "email": "sanjayjujjuri9@gmail.com",
        "platform": "Swiggy",
        "name": "Sanjay Jujjuri"
    },
    {
        "workerId": "SWG2008",
        "email": "sanzzogoud@gmail.com",
        "platform": "Swiggy",
        "name": "Sanzzo Goud"
    },
    {
        "workerId": "SWG2001",
        "email": "dorateja278@gmail.com",
        "platform": "Swiggy",
        "name": "Dora Teja"
    },
    {
        "workerId": "SWG2002",
        "email": "avishwakanth50@gmail.com",
        "platform": "Swiggy",
        "name": "Avishwakanth"
    },
    {
        "workerId": "SWG2003",
        "email": "devendraberre@gmail.com",
        "platform": "Swiggy",
        "name": "Devendra Berre"
    },
]

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new worker
    Request: {name, email, phone, city, zone, platform}
    Response: {user_id, name, email, phone, zone, platform, wallet_balance, token}
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'email', 'phone', 'city', 'zone', 'platform']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if user already exists by phone
        existing_user = User.query.filter_by(phone=data['phone']).first()
        if existing_user:
            logger.warning(f"❌ Registration attempt with existing phone: {data['phone']}")
            return jsonify({'error': 'User with this phone number already exists'}), 409

        # Check if email already exists
        existing_email = User.query.filter_by(email=data['email'].lower()).first()
        if existing_email:
            logger.warning(f"❌ Registration attempt with existing email: {data['email']}")
            return jsonify({'error': 'User with this email already exists'}), 409

        # Create new user
        new_user = User(
            name=data['name'],
            email=data['email'].lower(),
            phone=data['phone'],
            city=data['city'],
            zone=data['zone'],
            platform=data['platform']
        )

        db.session.add(new_user)
        db.session.flush()  # Get the user ID

        # Create empty wallet for the user
        wallet = Wallet(user_id=new_user.id, balance=0)
        db.session.add(wallet)

        db.session.commit()

        # Generate JWT token
        token = generate_token(new_user.id)

        logger.info(f"✅ New user registered: {new_user.name} ({new_user.id}) - {new_user.phone}")

        return jsonify({
            'user_id': new_user.id,
            'name': new_user.name,
            'email': new_user.email,
            'phone': new_user.phone,
            'city': new_user.city,
            'zone': new_user.zone,
            'platform': new_user.platform,
            'wallet_balance': 0,
            'token': token
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    Login existing worker with Worker ID + Email + Password
    Request: {worker_id, email, password}
    Response: {user_id, name, email, worker_id, city, zone, platform, wallet_balance, token, active_policy}
    """
    try:
        data = request.get_json()

        # Validate required fields
        if 'worker_id' not in data:
            return jsonify({'error': 'Worker ID is required'}), 400
        if 'email' not in data:
            return jsonify({'error': 'Email is required'}), 400
        if 'password' not in data:
            return jsonify({'error': 'Password is required'}), 400

        worker_id = data['worker_id'].strip().upper()
        email = data['email'].strip().lower()
        password = data['password'].strip()

        # Validate password (must be exactly "insurex123")
        if password != 'insurex123':
            logger.warning(f"🔴 Login attempt with incorrect password for worker {worker_id}")
            return jsonify({'error': 'Invalid password'}), 401

        # Find worker in VALID_WORKERS list
        worker = next((w for w in VALID_WORKERS if w['workerId'].upper() == worker_id), None)
        if not worker:
            logger.warning(f"🔴 Login attempt with invalid worker ID: {worker_id}")
            return jsonify({'error': 'Invalid Worker ID. Please register first.'}), 404

        # Verify email matches
        if worker['email'].lower() != email:
            logger.warning(f"🔴 Email mismatch for worker {worker_id}: expected {worker['email']}, got {email}")
            return jsonify({'error': 'Email does not match this Worker ID.'}), 400

        logger.info(f"✅ Worker verified: {worker_id} ({worker['name']})")

        # Try to find existing user in database by email
        user = User.query.filter_by(email=email).first()
        
        if not user:
            logger.info(f"📝 Creating new user record for {worker['name']} ({worker_id})")
            # Create new user if doesn't exist
            user = User(
                name=worker['name'],
                email=email,
                phone=worker_id,  # Store worker ID in phone field for compatibility
                city='Unknown',
                zone='Unknown',
                platform=worker['platform']
            )
            db.session.add(user)
            db.session.commit()
            logger.info(f"✅ User created: {user.name} ({user.id})")

        # Get wallet info
        wallet = Wallet.query.filter_by(user_id=user.id).first()
        if not wallet:
            wallet = Wallet(user_id=user.id, balance=0.0)
            db.session.add(wallet)
            db.session.commit()
        
        wallet_balance = float(wallet.balance) if wallet else 0.0

        # Check for active policy
        from app.models import Policy
        from datetime import datetime

        today = datetime.utcnow().date()
        active_policy = Policy.query.filter(
            Policy.user_id == user.id,
            Policy.status == 'active',
            Policy.start_date <= today,
            Policy.end_date >= today
        ).first()

        # Generate JWT token
        token = generate_token(user.id)

        logger.info(f"✅ User logged in: {user.name} ({user.id}) - Wallet: ₹{wallet_balance}")

        response_data = {
            'user_id': user.id,
            'name': user.name,
            'email': user.email,
            'worker_id': worker_id,
            'city': user.city,
            'zone': user.zone,
            'platform': worker['platform'],
            'wallet_balance': wallet_balance,
            'token': token,
            'has_active_policy': active_policy is not None
        }

        # Add policy details if exists
        if active_policy:
            response_data['active_policy'] = {
                'policy_id': active_policy.id,
                'premium': float(active_policy.premium),
                'start_date': active_policy.start_date.isoformat(),
                'end_date': active_policy.end_date.isoformat(),
                'days_remaining': (active_policy.end_date - today).days
            }

        return jsonify(response_data), 200

    except Exception as e:
        logger.error(f"❌ Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/me', methods=['GET'])
def get_current_user():
    """
    Get current authenticated user info
    Requires: Authorization header with Bearer token
    Response: User object
    """
    try:
        # Get token from header
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        # Verify token
        from app.utils import verify_token
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Get user
        user = User.query.get(payload['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 404

        return jsonify(user.to_dict()), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/verify-worker', methods=['POST'])
def verify_worker():
    """
    Verify worker ID against database and validate email
    Request: {workerId, email}
    Response: {verified, status, message, worker_name, platform}
    
    Status codes:
    - verified: Worker ID and email match
    - email_mismatch: Worker ID exists but email doesn't match
    - not_found: Worker ID not found in database
    - invalid: Input validation failed
    """
    try:
        data = request.get_json()
        
        # Validate input fields exist
        if not data or 'workerId' not in data or 'email' not in data:
            return jsonify({
                'verified': False,
                'status': 'invalid',
                'message': 'Worker ID and email are both required'
            }), 400
        
        worker_id = data['workerId'].strip().upper()
        email = data['email'].strip().lower()
        
        # Validate Worker ID not empty
        if not worker_id:
            return jsonify({
                'verified': False,
                'status': 'invalid',
                'message': 'Worker ID cannot be empty'
            }), 400
        
        # Validate email not empty
        if not email:
            return jsonify({
                'verified': False,
                'status': 'invalid',
                'message': 'Email cannot be empty'
            }), 400
        
        # Basic email format validation
        if '@' not in email or '.' not in email:
            return jsonify({
                'verified': False,
                'status': 'invalid',
                'message': 'Invalid email format'
            }), 400
        
        # Simulate database lookup delay (1-2 seconds)
        time.sleep(1.5)
        
        # Search for worker in database by workerId
        worker = None
        for w in VALID_WORKERS:
            if w['workerId'] == worker_id:
                worker = w
                break
        
        # Worker ID not found in database
        if not worker:
            logger.warning(f"⚠️ Worker ID not found: {worker_id}")
            return jsonify({
                'verified': False,
                'status': 'not_found',
                'message': f'Worker ID {worker_id} not found in system'
            }), 404
        
        # Worker ID found, check email match
        if worker['email'].lower() != email:
            logger.warning(f"⚠️ Email mismatch for Worker ID {worker_id}: Expected {worker['email']}, Got {email}")
            return jsonify({
                'verified': False,
                'status': 'email_mismatch',
                'message': 'Worker ID exists but email does not match our records'
            }), 400
        
        # Both Worker ID and email match!
        logger.info(f"✅ Worker verified: {worker_id} ({worker['email']}) - {worker['platform']}")
        
        return jsonify({
            'verified': True,
            'status': 'verified',
            'message': f'Worker {worker_id} verified successfully',
            'workerId': worker_id,
            'worker_name': worker['name'],
            'platform': worker['platform'],
            'email': worker['email']
        }), 200

    except Exception as e:
        logger.error(f"Worker verification error: {str(e)}")
        return jsonify({
            'verified': False,
            'status': 'error',
            'message': 'An error occurred during verification'
        }), 500


# ==================== OTP ENDPOINTS ====================

@bp.route('/send-otp', methods=['POST'])
def send_otp():
    """
    Send OTP to email for verification
    Request: {"email": "user@email.com"}
    Response: {"success": true, "message": "OTP sent successfully", "expiresIn": 300}
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        email = data['email'].strip().lower()
        
        # Validate email format
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Invalid email format'
            }), 400
        
        # Check if OTP was already sent recently
        if OTPService.is_otp_sent(email):
            remaining = OTPService.get_otp_expiry_remaining(email)
            return jsonify({
                'success': False,
                'message': f'OTP already sent. Please wait {remaining} seconds before requesting again.',
                'expiresIn': remaining
            }), 429
        
        # Generate OTP
        otp = OTPService.generate_otp()
        logger.info(f"🔐 Generated OTP for {email}: {otp}")
        
        # Store OTP
        OTPService.store_otp(email, otp)
        
        # Send OTP via email
        email_sent = OTPService.send_otp_email(email, otp)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'OTP sent successfully to your email',
                'expiresIn': 300  # 5 minutes in seconds
            }), 200
        else:
            # If email config is missing, return demo mode
            logger.warning(f"⚠️ Email not sent - Demo mode. OTP is: {otp}")
            return jsonify({
                'success': True,
                'message': 'Demo mode: OTP will be shown in console logs. Check backend logs.',
                'expiresIn': 300,
                'demo': True,
                'demoOtp': otp  # Only in dev mode
            }), 200

    except Exception as e:
        logger.error(f"❌ Error sending OTP: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to send OTP. Please try again.'
        }), 500


@bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    """
    Verify OTP for email
    Request: {"email": "user@email.com", "otp": "123456"}
    Response: {"verified": true, "message": "OTP verified successfully"}
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'otp' not in data:
            return jsonify({
                'verified': False,
                'message': 'Email and OTP are required'
            }), 400
        
        email = data['email'].strip().lower()
        otp = data['otp'].strip()
        
        # Validate OTP format (6 digits)
        if len(otp) != 6 or not otp.isdigit():
            return jsonify({
                'verified': False,
                'message': 'OTP must be 6 digits'
            }), 400
        
        # Verify OTP
        is_valid, message = OTPService.verify_otp(email, otp)
        
        if is_valid:
            return jsonify({
                'verified': True,
                'message': message
            }), 200
        else:
            return jsonify({
                'verified': False,
                'message': message
            }), 400

    except Exception as e:
        logger.error(f"❌ Error verifying OTP: {str(e)}")
        return jsonify({
            'verified': False,
            'message': 'Failed to verify OTP'
        }), 500


@bp.route('/resend-otp', methods=['POST'])
def resend_otp():
    """
    Resend OTP to email (bypasses rate limiting)
    Request: {"email": "user@email.com"}
    Response: {"success": true, "message": "New OTP sent"}
    """
    try:
        data = request.get_json()
        
        if not data or 'email' not in data:
            return jsonify({
                'success': False,
                'message': 'Email is required'
            }), 400
        
        email = data['email'].strip().lower()
        
        # Generate new OTP
        otp = OTPService.generate_otp()
        logger.info(f"🔐 Resending OTP for {email}: {otp}")
        
        # Store OTP
        OTPService.store_otp(email, otp)
        
        # Send OTP via email
        email_sent = OTPService.send_otp_email(email, otp)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'New OTP sent successfully to your email',
                'expiresIn': 300
            }), 200
        else:
            logger.warning(f"⚠️ Demo mode OTP resend. OTP is: {otp}")
            return jsonify({
                'success': True,
                'message': 'Demo mode: OTP will be shown in console logs.',
                'expiresIn': 300,
                'demo': True,
                'demoOtp': otp
            }), 200

    except Exception as e:
        logger.error(f"❌ Error resending OTP: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to resend OTP'
        }), 500


# ==================== WEATHER ENDPOINT ====================

@bp.route('/weather', methods=['POST'])
def get_weather():
    """
    Get weather data for given latitude and longitude
    Request: {"lat": -23.1815, "lon": 72.6313}
    Response: {"city": "Vadodara", "temperature": 32, "condition": "Rain", "wind": 10, "risk_level": "high"}
    """
    try:
        data = request.get_json()
        
        if not data or 'lat' not in data or 'lon' not in data:
            return jsonify({
                'error': 'Latitude and longitude are required',
                'city': 'Unknown',
                'temperature': 0,
                'condition': 'Unknown',
                'wind': 0,
                'risk_level': 'medium'
            }), 400
        
        lat = data['lat']
        lon = data['lon']
        
        # Validate coordinates
        try:
            lat = float(lat)
            lon = float(lon)
            if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
                raise ValueError("Invalid coordinates")
        except (ValueError, TypeError):
            return jsonify({
                'error': 'Invalid latitude or longitude',
                'city': 'Unknown',
                'temperature': 0,
                'condition': 'Unknown',
                'wind': 0,
                'risk_level': 'medium'
            }), 400
        
        # Get OpenWeather API key from environment
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            logger.warning("⚠️ OpenWeather API key not found in environment")
            return jsonify({
                'error': 'Weather API not configured',
                'city': 'Unknown',
                'temperature': 25,
                'condition': 'Clear',
                'wind': 5,
                'risk_level': 'low'
            }), 503
        
        # Fetch weather data from OpenWeatherMap
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        
        response = requests.get(url, timeout=5)
        
        if response.status_code != 200:
            logger.warning(f"⚠️ OpenWeather API error: {response.status_code}")
            return jsonify({
                'error': 'Weather service unavailable',
                'city': 'Unknown',
                'temperature': 25,
                'condition': 'Clear',
                'wind': 5,
                'risk_level': 'medium'
            }), 503
        
        weather_data = response.json()
        
        # Extract relevant data
        city = weather_data.get('name', 'Unknown')
        temperature = round(weather_data.get('main', {}).get('temp', 0))
        condition = weather_data.get('weather', [{}])[0].get('main', 'Unknown')
        wind_speed = round(weather_data.get('wind', {}).get('speed', 0), 1)
        
        # Determine risk level based on weather condition and other factors
        risk_level = 'low'
        if condition.lower() in ['rain', 'drizzle']:
            risk_level = 'medium'
        elif condition.lower() in ['thunderstorm', 'tornado', 'hurricane']:
            risk_level = 'high'
        elif temperature > 40:
            risk_level = 'medium'
        elif temperature > 45:
            risk_level = 'high'
        
        logger.info(f"✅ Weather fetched for {city}: {temperature}°C, {condition}, Wind: {wind_speed} m/s, Risk: {risk_level}")
        
        return jsonify({
            'city': city,
            'temperature': temperature,
            'condition': condition,
            'wind': wind_speed,
            'risk_level': risk_level,
            'lat': lat,
            'lon': lon
        }), 200
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Weather API request failed: {str(e)}")
        return jsonify({
            'error': 'Weather service unavailable',
            'city': 'Unknown',
            'temperature': 25,
            'condition': 'Clear',
            'wind': 5,
            'risk_level': 'medium'
        }), 503
    
    except Exception as e:
        logger.error(f"❌ Error fetching weather: {str(e)}")
        return jsonify({
            'error': 'Failed to get weather data',
            'city': 'Unknown',
            'temperature': 25,
            'condition': 'Clear',
            'wind': 5,
            'risk_level': 'medium'
        }), 500
