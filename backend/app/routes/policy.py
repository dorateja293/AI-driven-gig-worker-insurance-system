from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import User, Policy, Wallet, WalletTransaction
from app.services.premium_calculator import calculate_premium, get_coverage_triggers, get_max_payout

bp = Blueprint('policy', __name__, url_prefix='/api/policy')

@bp.route('/quote', methods=['GET'])
def get_quote():
    """
    Get policy quote for a user
    Query params: user_id
    Response: {user_id, zone, risk_score, weekly_premium, coverage_triggers, max_payout_per_event}
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        # Calculate premium
        premium_data = calculate_premium(user.zone, user.city)

        # Get coverage details
        coverage_triggers = get_coverage_triggers()
        max_payout = get_max_payout()

        return jsonify({
            'user_id': user.id,
            'zone': user.zone,
            'risk_score': premium_data['risk_score'],
            'weekly_premium': premium_data['premium'],
            'coverage_triggers': coverage_triggers,
            'max_payout_per_event': max_payout
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/purchase', methods=['POST'])
def purchase_policy():
    """
    Purchase a policy
    Request: {user_id, premium_amount}
    Response: {policy_id, status, start_date, end_date, premium_paid}
    """
    try:
        data = request.get_json()

        # Validate required fields
        if 'user_id' not in data or 'premium_amount' not in data:
            return jsonify({'error': 'user_id and premium_amount are required'}), 400

        user_id = data['user_id']
        premium_amount = float(data['premium_amount'])

        # Get user and wallet
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        wallet = Wallet.query.filter_by(user_id=user_id).first()
        if not wallet:
            return jsonify({'error': 'Wallet not found'}), 404

        # Check if user has sufficient balance
        if wallet.balance < premium_amount:
            return jsonify({'error': 'Insufficient wallet balance'}), 400

        # Check if user already has an active policy
        active_policy = Policy.query.filter_by(user_id=user_id, status='active').first()
        if active_policy:
            return jsonify({'error': 'User already has an active policy'}), 409

        # Calculate premium (verify amount)
        premium_data = calculate_premium(user.zone, user.city)

        # Debit wallet
        wallet.balance -= premium_amount
        wallet.updated_at = datetime.utcnow()

        # Create wallet transaction
        transaction = WalletTransaction(
            wallet_id=wallet.id,
            type='premium_paid',
            amount=-premium_amount,
            description=f'Premium payment for 7-day policy'
        )
        db.session.add(transaction)

        # Create policy (7 days from today)
        start_date = datetime.utcnow().date()
        end_date = start_date + timedelta(days=7)

        new_policy = Policy(
            user_id=user_id,
            risk_score=premium_data['risk_score'],
            premium=premium_amount,
            start_date=start_date,
            end_date=end_date,
            status='active'
        )
        db.session.add(new_policy)

        db.session.commit()

        return jsonify({
            'policy_id': new_policy.id,
            'status': new_policy.status,
            'start_date': new_policy.start_date.isoformat(),
            'end_date': new_policy.end_date.isoformat(),
            'premium_paid': premium_amount
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@bp.route('/status', methods=['GET'])
def get_policy_status():
    """
    Get active policy status for a user
    Query params: user_id
    Response: {policy_id, status, days_remaining, claims_this_week}
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Get active policy
        policy = Policy.query.filter_by(user_id=user_id, status='active').first()
        if not policy:
            return jsonify({'error': 'No active policy found'}), 404

        # Calculate days remaining
        today = datetime.utcnow().date()
        days_remaining = (policy.end_date - today).days

        # Count claims this week
        from app.models import Claim
        claims_count = Claim.query.filter_by(policy_id=policy.id).count()

        return jsonify({
            'policy_id': policy.id,
            'status': policy.status,
            'days_remaining': days_remaining,
            'claims_this_week': claims_count
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
