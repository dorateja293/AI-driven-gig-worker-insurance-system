"""
Event Simulator - Demo-Ready Event Triggering

Simulates real-world disruption events for testing and demo purposes.
Makes it easy to trigger events and see the full claim automation in action.
"""

from datetime import datetime
from app import db
from app.models import Event
from app.services.claim_engine import process_event
import logging

logger = logging.getLogger(__name__)


def trigger_event(event_type, zone, value=None, duration_hours=2.0):
    """
    Trigger a disruption event and automatically process claims.

    This is the MAGIC function for demos:
    - Creates the event
    - Runs claim automation
    - Returns full results

    Args:
        event_type (str): 'HEAT', 'RAIN', 'OUTAGE', 'SMOG', 'BLACKOUT'
        zone (str): Zone identifier (e.g., 'Zone-A')
        value (str, optional): Event value (e.g., '45°C', '60mm')
        duration_hours (float): Event duration in hours

    Returns:
        dict: Complete event and claim processing results
    """
    logger.info(f"⚡ Triggering {event_type} event in {zone}")

    # Map event types to standard format
    event_type_map = {
        'HEAT': 'extreme_heat',
        'RAIN': 'heavy_rain',
        'OUTAGE': 'platform_outage',
        'SMOG': 'smog',
        'BLACKOUT': 'blackout'
    }

    standard_event_type = event_type_map.get(event_type.upper(), event_type.lower())

    # Generate default values if not provided
    if not value:
        value = generate_event_value(standard_event_type)

    # Create event record
    event = Event(
        zone=zone,
        event_type=standard_event_type,
        trigger_value=value,
        duration=duration_hours,
        detected_at=datetime.utcnow()
    )

    db.session.add(event)
    db.session.commit()

    logger.info(f"✅ Event created: {event.id} - {standard_event_type} in {zone}")

    # Run claim automation
    logger.info("🤖 Starting automatic claim processing...")
    claim_results = process_event(event.id)

    # Combine event and claim data
    result = {
        'event': {
            'event_id': event.id,
            'type': event.event_type,
            'zone': event.zone,
            'value': event.trigger_value,
            'duration_hours': float(event.duration),
            'timestamp': event.detected_at.isoformat()
        },
        'automation': claim_results,
        'summary': generate_summary(event, claim_results)
    }

    logger.info(f"🎉 Event processing complete: {result['summary']}")

    return result


def generate_event_value(event_type):
    """
    Generate realistic event values for demo.

    Args:
        event_type (str): Event type

    Returns:
        str: Event value
    """
    values = {
        'extreme_heat': '45°C for 2.5 hours',
        'heavy_rain': '62mm in 3 hours',
        'platform_outage': '35 minutes downtime',
        'smog': 'AQI 350 (Severe)',
        'blackout': '2 hours power cut'
    }

    return values.get(event_type, 'Event detected')


def generate_summary(event, claim_results):
    """
    Generate human-readable summary for demo narration.

    Args:
        event: Event object
        claim_results: Results from claim automation

    Returns:
        str: Demo-ready summary
    """
    event_names = {
        'extreme_heat': 'Extreme heat',
        'heavy_rain': 'Heavy rainfall',
        'platform_outage': 'Platform outage',
        'smog': 'Severe smog',
        'blackout': 'Power blackout'
    }

    event_name = event_names.get(event.event_type, event.event_type)

    summary_parts = [
        f"{event_name} detected in {event.zone}",
        f"{claim_results['eligible_workers']} workers affected",
        f"{claim_results['approved']} claims approved",
        f"₹{int(claim_results['total_payout'])} paid out instantly"
    ]

    if claim_results['flagged'] > 0:
        summary_parts.append(f"{claim_results['flagged']} suspicious claims flagged")

    return " → ".join(summary_parts)


def trigger_preset_demo(zone='Zone-D'):
    """
    Trigger a preset demo scenario with realistic values.

    Perfect for quick demos.

    Args:
        zone (str): Zone to trigger event in

    Returns:
        dict: Event and claim results
    """
    logger.info(f"🎬 Running preset demo scenario in {zone}")

    # Trigger extreme heat (high impact)
    result = trigger_event(
        event_type='HEAT',
        zone=zone,
        value='45°C',
        duration_hours=2.5
    )

    return result


def simulate_multiple_events(zone, count=3):
    """
    Simulate multiple events for stress testing.

    Args:
        zone (str): Zone to trigger events in
        count (int): Number of events to trigger

    Returns:
        list: Results from all events
    """
    logger.info(f"📊 Simulating {count} events in {zone}")

    event_types = ['HEAT', 'RAIN', 'OUTAGE']
    results = []

    for i in range(count):
        event_type = event_types[i % len(event_types)]
        result = trigger_event(
            event_type=event_type,
            zone=zone
        )
        results.append(result)

    logger.info(f"✅ Simulated {count} events successfully")

    return results


def get_event_statistics(zone=None):
    """
    Get statistics about events and claims.

    Args:
        zone (str, optional): Filter by zone

    Returns:
        dict: Event statistics
    """
    from app.models import Claim

    query = Event.query
    if zone:
        query = query.filter_by(zone=zone)

    events = query.all()

    total_events = len(events)
    total_claims = Claim.query.count()
    approved_claims = Claim.query.filter_by(status='paid').count()
    flagged_claims = Claim.query.filter_by(status='flagged').count()

    # Calculate total payout
    from sqlalchemy import func
    total_payout = db.session.query(
        func.sum(Claim.payout_amount)
    ).filter(Claim.status == 'paid').scalar() or 0

    return {
        'total_events': total_events,
        'total_claims': total_claims,
        'approved_claims': approved_claims,
        'flagged_claims': flagged_claims,
        'approval_rate': round((approved_claims / total_claims * 100) if total_claims > 0 else 0, 1),
        'total_payout': float(total_payout),
        'avg_payout_per_claim': round(float(total_payout) / approved_claims, 2) if approved_claims > 0 else 0
    }
