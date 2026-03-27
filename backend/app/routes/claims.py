from flask import Blueprint, request, jsonify
from app import db
from app.models import Claim, Event, User

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
