from flask import Blueprint, request, jsonify
from datetime import datetime
from app import db
from app.models import Event

bp = Blueprint('events', __name__, url_prefix='/api/events')

@bp.route('', methods=['GET'])
def get_events():
    """
    Get events for a specific zone
    Query params: zone (optional)
    Response: {events[]}
    """
    try:
        zone = request.args.get('zone')

        # Build query
        query = Event.query

        # Filter by zone if provided
        if zone:
            query = query.filter_by(zone=zone)

        # Get events ordered by most recent
        events = query.order_by(Event.detected_at.desc()).limit(50).all()

        return jsonify({
            'events': [event.to_dict() for event in events]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/simulate', methods=['POST'])
def simulate_event():
    """
    Simulate a disruption event (for testing)
    Request: {zone, type, value, duration_hours}
    Response: {event_id, zone, type, value, duration_hours}
    """
    try:
        data = request.get_json()

        # Validate required fields
        required_fields = ['zone', 'type', 'value', 'duration_hours']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        # Create event
        new_event = Event(
            zone=data['zone'],
            event_type=data['type'],
            trigger_value=str(data['value']),
            duration=float(data['duration_hours']),
            detected_at=datetime.utcnow()
        )

        db.session.add(new_event)
        db.session.commit()

        # Push to Redis queue for claim processing
        try:
            from app.services.queue_service import push_event_to_queue
            push_event_to_queue(new_event.id)
        except Exception as queue_error:
            print(f"Warning: Could not push to queue: {queue_error}")

        return jsonify({
            'event_id': new_event.id,
            'zone': new_event.zone,
            'type': new_event.event_type,
            'value': new_event.trigger_value,
            'duration_hours': float(new_event.duration)
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
