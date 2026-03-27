"""
ML API Routes - Integration with Premium Calculator, Fraud Detector, and Predictor

These endpoints expose ML functionality to the frontend and other services.
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import sys
import os

# Add ml directory to path
ml_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml')
sys.path.insert(0, ml_path)

from ml.premium_calculator import calculate_premium_for_zone, calculate_premium
from ml.fraud_detector import detect_fraud
from ml.predictor import predict_disruption, get_insurance_urgency

from app import db
from app.models import User, Policy, Claim, Event, GPSLog, ActivityLog, Wallet, WalletTransaction

bp = Blueprint('ml', __name__, url_prefix='/api/ml')


@bp.route('/calculate-premium', methods=['POST'])
def calculate_premium_route():
    """
    Calculate insurance premium using ML risk scoring.

    Request: {
        "zone": "Zone-A",  # OR provide individual parameters:
        "heat_days": int (optional),
        "rain_days": int (optional),
        "zone_risk": float (optional),
        "season_factor": float (optional)
    }

    Response: {
        "risk_score": float,
        "premium": int,
        "breakdown": {...}
    }
    """
    try:
        data = request.get_json()

        # Option 1: Calculate by zone
        if 'zone' in data:
            zone = data['zone']
            season_factor = data.get('season_factor', 1.0)
            result = calculate_premium_for_zone(zone, season_factor)

        # Option 2: Calculate by individual parameters
        else:
            heat_days = data.get('heat_days', 10)
            rain_days = data.get('rain_days', 10)
            zone_risk = data.get('zone_risk', 0.5)
            season_factor = data.get('season_factor', 1.0)

            result = calculate_premium(heat_days, rain_days, zone_risk, season_factor)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/check-fraud', methods=['POST'])
def check_fraud_route():
    """
    Check if a claim is fraudulent using ML anomaly detection.

    Request: {
        "user_id": "usr_xxx",
        "event_id": "evt_xxx",
        "gps_movement": float or list,  # km or coordinates
        "orders_completed": int,
        "is_online": bool,
        "nearby_claims_count": int (optional)
    }

    Response: {
        "fraud_score": float,
        "risk_level": "LOW|MEDIUM|HIGH",
        "action": "APPROVE|REVIEW|FLAG",
        "reasons": [...]
    }
    """
    try:
        data = request.get_json()

        user_id = data.get('user_id')
        event_id = data.get('event_id')

        # Get event info
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        # Calculate GPS movement if not provided
        gps_movement = data.get('gps_movement')
        if gps_movement is None:
            # Get GPS logs from last 4 hours before event
            time_window = event.detected_at - timedelta(hours=4)
            gps_logs = GPSLog.query.filter(
                GPSLog.user_id == user_id,
                GPSLog.logged_at >= time_window,
                GPSLog.logged_at <= event.detected_at
            ).order_by(GPSLog.logged_at).all()

            if gps_logs:
                gps_coords = [(float(log.latitude), float(log.longitude)) for log in gps_logs]
                gps_movement = gps_coords
            else:
                gps_movement = 0.0

        # Get activity data if not provided
        orders_completed = data.get('orders_completed')
        is_online = data.get('is_online')

        if orders_completed is None or is_online is None:
            time_window = event.detected_at - timedelta(hours=6)
            activity_logs = ActivityLog.query.filter(
                ActivityLog.user_id == user_id,
                ActivityLog.logged_at >= time_window,
                ActivityLog.logged_at <= event.detected_at
            ).all()

            if activity_logs:
                orders_completed = sum(log.orders_count for log in activity_logs)
                is_online = any(log.status in ['online', 'delivering'] for log in activity_logs)
            else:
                orders_completed = 0
                is_online = False

        # Count nearby claims
        nearby_claims_count = data.get('nearby_claims_count')
        if nearby_claims_count is None:
            nearby_claims_count = Claim.query.filter_by(event_id=event_id).count()

        # Run fraud detection
        result = detect_fraud(
            gps_movement=gps_movement,
            orders_completed=orders_completed,
            is_online=is_online,
            claim_time=datetime.utcnow(),
            event_time=event.detected_at,
            nearby_claims_count=nearby_claims_count
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/predict-risk', methods=['POST'])
def predict_risk_route():
    """
    Predict disruption risk for next period using recent weather data.

    Request: {
        "zone": "Zone-A",  # optional, will use mock data
        "last_7_days_weather": {  # optional
            "temperatures": [float, ...],
            "rainfall": [float, ...]
        }
    }

    Response: {
        "heat_risk": float,
        "rain_risk": float,
        "overall_risk": float,
        "recommendation": "BUY_POLICY|SAFE",
        "forecast": {...}
    }
    """
    try:
        data = request.get_json()

        # Get weather data
        last_7_days_weather = data.get('last_7_days_weather')

        # If not provided, generate mock data for demo
        if not last_7_days_weather:
            zone = data.get('zone', 'Zone-A')
            last_7_days_weather = generate_mock_weather(zone)

        # Run prediction
        result = predict_disruption(last_7_days_weather)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/insurance-urgency', methods=['POST'])
def insurance_urgency_route():
    """
    Get insurance purchase urgency score (0-10).

    Request: {
        "zone": "Zone-A",
        "last_7_days_weather": {...} (optional)
    }

    Response: {
        "urgency_score": int,
        "urgency_level": str,
        "action": str,
        "prediction_details": {...}
    }
    """
    try:
        data = request.get_json()

        last_7_days_weather = data.get('last_7_days_weather')

        if not last_7_days_weather:
            zone = data.get('zone', 'Zone-A')
            last_7_days_weather = generate_mock_weather(zone)

        result = get_insurance_urgency(last_7_days_weather)

        return jsonify(result), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/auto-claim', methods=['POST'])
def auto_claim_route():
    """
    AUTO-CLAIM FLOW: Process automatic claim for event with fraud detection.

    Request: {
        "user_id": "usr_xxx",
        "event_id": "evt_xxx"
    }

    Response: {
        "claim_id": str,
        "status": "approved|flagged|rejected",
        "payout_amount": float,
        "fraud_analysis": {...}
    }
    """
    try:
        data = request.get_json()

        user_id = data['user_id']
        event_id = data['event_id']

        # 1. Check if user has active policy
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        today = datetime.utcnow().date()
        active_policy = Policy.query.filter(
            Policy.user_id == user_id,
            Policy.status == 'active',
            Policy.start_date <= today,
            Policy.end_date >= today
        ).first()

        if not active_policy:
            return jsonify({'error': 'No active policy found'}), 400

        # 2. Check if disruption event exists
        event = Event.query.get(event_id)
        if not event:
            return jsonify({'error': 'Event not found'}), 404

        # Verify zone matches
        if event.zone != user.zone:
            return jsonify({'error': 'Event zone does not match user zone'}), 400

        # 3. Check if claim already exists
        existing_claim = Claim.query.filter_by(
            user_id=user_id,
            event_id=event_id
        ).first()

        if existing_claim:
            return jsonify({'error': 'Claim already exists', 'claim_id': existing_claim.id}), 409

        # 4. Run fraud detection
        # Get GPS movement data
        time_window = event.detected_at - timedelta(hours=4)
        gps_logs = GPSLog.query.filter(
            GPSLog.user_id == user_id,
            GPSLog.logged_at >= time_window,
            GPSLog.logged_at <= event.detected_at
        ).order_by(GPSLog.logged_at).all()

        gps_movement = [(float(log.latitude), float(log.longitude)) for log in gps_logs] if gps_logs else 0.0

        # Get activity data
        activity_window = event.detected_at - timedelta(hours=6)
        activity_logs = ActivityLog.query.filter(
            ActivityLog.user_id == user_id,
            ActivityLog.logged_at >= activity_window,
            ActivityLog.logged_at <= event.detected_at
        ).all()

        orders_completed = sum(log.orders_count for log in activity_logs) if activity_logs else 0
        is_online = any(log.status in ['online', 'delivering'] for log in activity_logs) if activity_logs else False

        # Count nearby claims for fraud ring detection
        nearby_claims_count = Claim.query.filter_by(event_id=event_id).count()

        # Run fraud detector
        fraud_result = detect_fraud(
            gps_movement=gps_movement,
            orders_completed=orders_completed,
            is_online=is_online,
            claim_time=datetime.utcnow(),
            event_time=event.detected_at,
            nearby_claims_count=nearby_claims_count
        )

        # 5. Determine payout amount based on event type
        payout_amount = 200  # Default
        if event.event_type == 'platform_outage':
            payout_amount = 150

        # 6. Create claim based on fraud result
        claim = Claim(
            user_id=user_id,
            policy_id=active_policy.id,
            event_id=event_id,
            payout_amount=payout_amount,
            fraud_score=fraud_result['fraud_score'],
            risk_level=fraud_result['risk_level'],
            fraud_reason='; '.join(fraud_result['reasons']) if fraud_result['reasons'] else None
        )

        # 7. Set status based on fraud action
        if fraud_result['action'] == 'APPROVE':
            claim.status = 'approved'

            # Execute payout immediately
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if wallet:
                wallet.balance += payout_amount

                # Create transaction
                transaction = WalletTransaction(
                    wallet_id=wallet.id,
                    type='claim_payout',
                    amount=payout_amount,
                    description=f"Payout for {event.event_type} - Claim {claim.id}"
                )
                db.session.add(transaction)

                claim.status = 'paid'

        elif fraud_result['action'] == 'REVIEW':
            claim.status = 'pending'

        else:  # FLAG
            claim.status = 'flagged'

        db.session.add(claim)
        db.session.commit()

        return jsonify({
            'claim_id': claim.id,
            'status': claim.status,
            'payout_amount': float(payout_amount),
            'fraud_analysis': fraud_result
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def generate_mock_weather(zone):
    """Generate mock weather data for demo purposes"""
    import random

    # Zone-specific weather patterns
    zone_patterns = {
        'Zone-A': {'base_temp': 38, 'base_rain': 15},
        'Zone-B': {'base_temp': 42, 'base_rain': 25},
        'Zone-C': {'base_temp': 32, 'base_rain': 8},
        'Zone-D': {'base_temp': 44, 'base_rain': 30},
    }

    pattern = zone_patterns.get(zone, {'base_temp': 35, 'base_rain': 15})

    temperatures = [pattern['base_temp'] + random.uniform(-3, 5) for _ in range(7)]
    rainfall = [max(0, pattern['base_rain'] + random.uniform(-10, 15)) for _ in range(7)]

    return {
        'temperatures': [round(t, 1) for t in temperatures],
        'rainfall': [round(r, 1) for r in rainfall]
    }
