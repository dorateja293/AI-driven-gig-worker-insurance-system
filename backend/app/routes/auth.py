from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Wallet
from app.utils import generate_token
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@bp.route('/register', methods=['POST'])
def register():
    """
    Register a new worker
    Request: {name, phone, city, zone, platform}
    Response: {user_id, name, phone, zone, platform, wallet_balance, token}
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['name', 'phone', 'city', 'zone', 'platform']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Check if user already exists
        existing_user = User.query.filter_by(phone=data['phone']).first()
        if existing_user:
            logger.warning(f"Registration attempt with existing phone: {data['phone']}")
            return jsonify({'error': 'User with this phone number already exists'}), 409

        # Create new user
        new_user = User(
            name=data['name'],
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
            'phone': new_user.phone,
            'city': new_user.city,
            'zone': new_user.zone,
            'platform': new_user.platform,
            'wallet_balance': 0,
            'token': token
        }), 201

    except Exception as e:
        db.session.rollback()
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/login', methods=['POST'])
def login():
    """
    Login existing worker
    Request: {phone}
    Response: {user_id, name, phone, zone, platform, wallet_balance, token, active_policy}
    """
    try:
        data = request.get_json()

        # Validate required fields
        if 'phone' not in data:
            return jsonify({'error': 'Phone number is required'}), 400

        # Find user by phone
        user = User.query.filter_by(phone=data['phone']).first()
        if not user:
            logger.warning(f"Login attempt with non-existent phone: {data['phone']}")
            return jsonify({'error': 'User not found. Please register first.'}), 404

        # Get wallet info
        wallet = Wallet.query.filter_by(user_id=user.id).first()
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
            'phone': user.phone,
            'city': user.city,
            'zone': user.zone,
            'platform': user.platform,
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
        logger.error(f"Login error: {str(e)}")
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
