from flask import Blueprint, request, jsonify
from app.models import Claim, User, Event
from app import db

bp = Blueprint('fraud', __name__, url_prefix='/api/fraud')

@bp.route('/flagged', methods=['GET'])
def get_flagged_claims():
    """
    Get all flagged claims (admin endpoint)
    Query params: risk_level (optional: 'medium', 'high', 'critical')
    Response: {flagged_claims[]}
    """
    try:
        risk_level = request.args.get('risk_level')

        # Build query for flagged or high fraud score claims
        query = Claim.query

        if risk_level == 'high':
            # fraud_score >= 0.6
            query = query.filter(Claim.fraud_score >= 0.6)
        elif risk_level == 'medium':
            # 0.3 <= fraud_score < 0.6
            query = query.filter(Claim.fraud_score >= 0.3, Claim.fraud_score < 0.6)
        elif risk_level == 'critical':
            # fraud_score >= 0.8
            query = query.filter(Claim.fraud_score >= 0.8)
        else:
            # All flagged (fraud_score >= 0.3 or status='flagged')
            query = query.filter(
                db.or_(
                    Claim.fraud_score >= 0.3,
                    Claim.status == 'flagged'
                )
            )

        # Get claims
        claims = query.order_by(Claim.fraud_score.desc()).all()

        # Build response
        flagged_claims = []
        for claim in claims:
            user = User.query.get(claim.user_id)
            event = Event.query.get(claim.event_id)

            # Determine risk level
            if claim.fraud_score >= 0.8:
                risk = 'critical'
            elif claim.fraud_score >= 0.6:
                risk = 'high'
            elif claim.fraud_score >= 0.3:
                risk = 'medium'
            else:
                risk = 'low'

            flagged_claims.append({
                'claim_id': claim.id,
                'user_id': claim.user_id,
                'user_name': user.name if user else 'Unknown',
                'user_phone': user.phone if user else 'Unknown',
                'zone': user.zone if user else 'Unknown',
                'event_type': event.event_type if event else 'unknown',
                'payout_amount': float(claim.payout_amount),
                'fraud_score': float(claim.fraud_score),
                'risk_level': risk,
                'reason': claim.fraud_reason,
                'status': claim.status,
                'timestamp': claim.created_at.isoformat()
            })

        return jsonify({
            'flagged_claims': flagged_claims,
            'total': len(flagged_claims)
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
