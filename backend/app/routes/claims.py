from flask import Blueprint, request, jsonify
from app import db
from app.models import Claim, Event, User, Policy, Wallet
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

bp = Blueprint('claims', __name__, url_prefix='/api/claims')

@bp.route('', methods=['GET'])
def get_user_claims():
    """
    Get claims for a specific user
    Query params: user_id
    Response: {claims[]}
    """
    try:
        user_id = request.args.get('user_id')
        if not user_id:
            return jsonify({'error': 'user_id is required'}), 400

        # Get claims for the user
        claims = Claim.query.filter_by(user_id=user_id).order_by(
            Claim.created_at.desc()
        ).all()

        # Build response with event details
        claims_list = []
        for claim in claims:
            event = Event.query.get(claim.event_id)
            claim_dict = {
                'claim_id': claim.id,
                'event_type': event.event_type if event else 'unknown',
                'trigger_value': event.trigger_value if event else 'N/A',
                'payout_amount': float(claim.payout_amount),
                'status': claim.status,
                'timestamp': claim.created_at.isoformat()
            }
            claims_list.append(claim_dict)

        return jsonify({
            'claims': claims_list
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/admin/all', methods=['GET'])
def get_all_claims():
    """
    Get all claims (admin endpoint)
    Query params: page (default 1), per_page (default 20), status (optional filter)
    Response: {claims[], total, page, per_page}
    """
    try:
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status_filter = request.args.get('status')

        # Build query
        query = Claim.query

        # Apply status filter if provided
        if status_filter:
            query = query.filter_by(status=status_filter)

        # Paginate
        pagination = query.order_by(Claim.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )

        # Build response
        claims_list = []
        for claim in pagination.items:
            user = User.query.get(claim.user_id)
            event = Event.query.get(claim.event_id)

            claim_dict = {
                'claim_id': claim.id,
                'user_id': claim.user_id,
                'user_name': user.name if user else 'Unknown',
                'user_phone': user.phone if user else 'Unknown',
                'zone': user.zone if user else 'Unknown',
                'event_type': event.event_type if event else 'unknown',
                'trigger_value': event.trigger_value if event else 'N/A',
                'payout_amount': float(claim.payout_amount),
                'status': claim.status,
                'fraud_score': float(claim.fraud_score),
                'fraud_reason': claim.fraud_reason,
                'timestamp': claim.created_at.isoformat()
            }
            claims_list.append(claim_dict)

        return jsonify({
            'claims': claims_list,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'total_pages': pagination.pages
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/check-weather-trigger', methods=['POST'])
def check_weather_trigger():
    """
    Check if weather conditions trigger automatic claim
    Request: {user_id, weather_condition, temperature, city, lat, lon}
    Response: {claimTriggered, amount, reason, claim_id}
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({'error': 'user_id is required'}), 400
        
        user_id = data['user_id']
        weather_condition = data.get('weather_condition', 'Unknown').strip()
        temperature = data.get('temperature', 0)
        city = data.get('city', 'Unknown')
        
        # Get user
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check if user has active policy
        today = datetime.utcnow().date()
        active_policy = Policy.query.filter(
            Policy.user_id == user_id,
            Policy.status == 'active',
            Policy.start_date <= today,
            Policy.end_date >= today
        ).first()
        
        if not active_policy:
            logger.warning(f"⚠️ No active policy for user {user_id}")
            return jsonify({
                'claimTriggered': False,
                'reason': 'No active policy'
            }), 200
        
        # Evaluate weather risk level
        risk_level = 'LOW'
        claim_amount = 0
        trigger_event_type = None
        should_trigger_claim = False
        
        weather_lower = weather_condition.lower()
        
        # HIGH RISK: Thunderstorm, Flood, Heavy Rain
        if any(x in weather_lower for x in ['thunderstorm', 'severe', 'storm', 'flood', 'heavy rain', 'extreme']):
            risk_level = 'HIGH'
            claim_amount = 750
            trigger_event_type = 'severe_weather_disruption'
            should_trigger_claim = True
            logger.info(f"⚠️⚠️⚠️ HIGH RISK WEATHER for {user.name}: {weather_condition}")
        
        # MEDIUM RISK: Rain, Wind
        elif any(x in weather_lower for x in ['rain', 'wind', 'drizzle', 'showers']):
            risk_level = 'MEDIUM'
            claim_amount = 500
            trigger_event_type = 'moderate_weather_disruption'
            logger.info(f"⚠️ MEDIUM RISK WEATHER for {user.name}: {weather_condition}")
        
        # LOW RISK: Clear, Sunny, Cloudy
        else:
            risk_level = 'LOW'
            claim_amount = 0
            logger.info(f"✅ LOW RISK WEATHER for {user.name}: {weather_condition}")
        
        # Only trigger claims for HIGH risk
        if not should_trigger_claim:
            return jsonify({
                'claimTriggered': False,
                'riskLevel': risk_level,
                'temperature': temperature,
                'city': city,
                'reason': f'{risk_level} risk weather detected'
            }), 200
        
        # Check if claim already triggered in last 1 hour for same weather condition
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        recent_claim = Claim.query.join(Event).filter(
            Claim.user_id == user_id,
            Event.event_type == trigger_event_type,
            Claim.created_at >= one_hour_ago
        ).first()
        
        if recent_claim:
            logger.warning(f"⏸️ Claim already triggered recently for {user.name}")
            return jsonify({
                'claimTriggered': False,
                'riskLevel': risk_level,
                'reason': 'Claim already triggered within last hour',
                'lastClaimTime': recent_claim.created_at.isoformat()
            }), 200
        
        # CREATE AUTOMATIC CLAIM
        try:
            # Create event record
            event = Event(
                zone=user.zone,
                event_type=trigger_event_type,
                trigger_value=f"{weather_condition} ({temperature}°C)",
                duration=0.5,  # 30 minutes
                detected_at=datetime.utcnow()
            )
            db.session.add(event)
            db.session.flush()
            
            # Create claim
            claim = Claim(
                user_id=user_id,
                policy_id=active_policy.id,
                event_id=event.id,
                payout_amount=claim_amount,
                status='approved',  # Auto-approved for weather-triggered claims
                risk_level=risk_level,
                fraud_score=0,
                fraud_reason=None
            )
            db.session.add(claim)
            db.session.flush()
            
            # Update wallet
            wallet = Wallet.query.filter_by(user_id=user_id).first()
            if wallet:
                wallet.balance = float(wallet.balance) + claim_amount
                db.session.add(wallet)
            
            db.session.commit()
            
            logger.info(f"✅✅✅ AUTO CLAIM TRIGGERED for {user.name}: ₹{claim_amount} ({weather_condition})")
            
            return jsonify({
                'claimTriggered': True,
                'claimId': claim.id,
                'amount': claim_amount,
                'riskLevel': risk_level,
                'temperature': temperature,
                'city': city,
                'condition': weather_condition,
                'reason': f'Automatic claim triggered due to {weather_condition}',
                'newBalance': float(wallet.balance) if wallet else 0
            }), 200
        
        except Exception as claim_err:
            db.session.rollback()
            logger.error(f"❌ Error creating auto-claim: {str(claim_err)}")
            return jsonify({
                'error': f'Failed to create claim: {str(claim_err)}'
            }), 500
    
    except Exception as e:
        logger.error(f"❌ Error in check_weather_trigger: {str(e)}")
        return jsonify({'error': str(e)}), 500
