"""
Claim Automation Engine - Core Feature

Automatically processes claims for all affected workers when an event occurs.
This is the heart of the parametric insurance system.
"""

from datetime import datetime, timedelta
from app import db
from app.models import User, Policy, Event, Claim, Wallet, WalletTransaction, GPSLog, ActivityLog
from ml.fraud_detector import detect_fraud
import logging

logger = logging.getLogger(__name__)


def process_event(event_id):
    """
    Automatically process claims for all workers affected by an event.

    This is the CORE AUTOMATION that makes parametric insurance work:
    1. Find all workers in affected zone
    2. Check who has active policies
    3. Run fraud detection
    4. Auto-approve or flag claims
    5. Execute instant payouts

    Args:
        event_id (str): The event ID to process

    Returns:
        dict: {
            'event_id': str,
            'zone': str,
            'event_type': str,
            'total_workers_in_zone': int,
            'eligible_workers': int,
            'claims_created': int,
            'approved': int,
            'flagged': int,
            'under_review': int,
            'total_payout': float,
            'processing_time_ms': int
        }
    """
    start_time = datetime.utcnow()

    logger.info(f"🚀 Starting claim automation for event {event_id}")

    # Get event details
    event = Event.query.get(event_id)
    if not event:
        logger.error(f"Event {event_id} not found")
        return {'error': 'Event not found'}

    logger.info(f"📍 Event: {event.event_type} in {event.zone} - {event.trigger_value}")

    # Find all workers in affected zone
    workers_in_zone = User.query.filter_by(zone=event.zone).all()
    logger.info(f"👥 Found {len(workers_in_zone)} workers in {event.zone}")

    # Determine payout amount
    payout_amount = get_payout_for_event(event.event_type)

    # Find workers with active policies
    today = datetime.utcnow().date()
    eligible_workers = []

    for worker in workers_in_zone:
        active_policy = Policy.query.filter(
            Policy.user_id == worker.id,
            Policy.status == 'active',
            Policy.start_date <= today,
            Policy.end_date >= today
        ).first()

        if active_policy:
            # Check if claim already exists
            existing_claim = Claim.query.filter_by(
                user_id=worker.id,
                event_id=event_id
            ).first()

            if not existing_claim:
                eligible_workers.append((worker, active_policy))

    logger.info(f"✅ {len(eligible_workers)} workers eligible for claims")

    # Process claims
    results = {
        'event_id': event_id,
        'zone': event.zone,
        'event_type': event.event_type,
        'total_workers_in_zone': len(workers_in_zone),
        'eligible_workers': len(eligible_workers),
        'claims_created': 0,
        'approved': 0,
        'flagged': 0,
        'under_review': 0,
        'total_payout': 0.0
    }

    if len(eligible_workers) == 0:
        logger.warning("⚠️ No eligible workers found")
        processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
        results['processing_time_ms'] = int(processing_time)
        return results

    # Run fraud detection and create claims
    logger.info("🔍 Running fraud detection on all claims...")

    for worker, policy in eligible_workers:
        # Get worker data for fraud detection
        fraud_data = get_worker_fraud_data(worker.id, event.detected_at)

        # Count nearby claims (for cluster detection)
        nearby_claims = Claim.query.filter_by(event_id=event_id).count()

        # Run fraud detection
        fraud_result = detect_fraud(
            gps_movement=fraud_data['gps_distance'],
            orders_completed=fraud_data['orders_completed'],
            is_online=fraud_data['is_online'],
            claim_time=datetime.utcnow(),
            event_time=event.detected_at,
            nearby_claims_count=nearby_claims
        )

        # Create claim
        claim = Claim(
            user_id=worker.id,
            policy_id=policy.id,
            event_id=event_id,
            payout_amount=payout_amount,
            fraud_score=fraud_result['fraud_score'],
            risk_level=fraud_result['risk_level'],
            fraud_reason='; '.join(fraud_result['reasons']) if fraud_result['reasons'] else None
        )

        # Decide action based on fraud score
        if fraud_result['action'] == 'APPROVE':
            claim.status = 'approved'
            results['approved'] += 1

            # Execute instant payout
            wallet = Wallet.query.filter_by(user_id=worker.id).first()
            if wallet:
                wallet.balance += payout_amount

                # Create transaction
                transaction = WalletTransaction(
                    wallet_id=wallet.id,
                    type='claim_payout',
                    amount=payout_amount,
                    description=f"Auto-payout: {event.event_type} - {event.trigger_value}"
                )
                db.session.add(transaction)

                claim.status = 'paid'
                results['total_payout'] += float(payout_amount)

                logger.info(f"💰 Paid ₹{payout_amount} to {worker.name} (fraud: {fraud_result['fraud_score']})")

        elif fraud_result['action'] == 'REVIEW':
            claim.status = 'pending'
            results['under_review'] += 1
            logger.info(f"⏳ Claim for {worker.name} under review (fraud: {fraud_result['fraud_score']})")

        else:  # FLAG
            claim.status = 'flagged'
            results['flagged'] += 1
            logger.warning(f"🚩 Claim for {worker.name} flagged (fraud: {fraud_result['fraud_score']})")

        db.session.add(claim)
        results['claims_created'] += 1

    # Commit all changes
    db.session.commit()

    processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
    results['processing_time_ms'] = int(processing_time)

    logger.info(f"✅ Claim automation complete: {results['approved']} approved, {results['flagged']} flagged, ₹{results['total_payout']} paid out")
    logger.info(f"⚡ Processing time: {results['processing_time_ms']}ms")

    return results


def get_worker_fraud_data(user_id, event_time):
    """
    Gather worker data for fraud detection.

    Args:
        user_id (str): Worker user ID
        event_time (datetime): When event occurred

    Returns:
        dict: Fraud detection data
    """
    # Get GPS movement (last 4 hours before event)
    time_window = event_time - timedelta(hours=4)
    gps_logs = GPSLog.query.filter(
        GPSLog.user_id == user_id,
        GPSLog.logged_at >= time_window,
        GPSLog.logged_at <= event_time
    ).order_by(GPSLog.logged_at).all()

    if gps_logs:
        gps_coords = [(float(log.latitude), float(log.longitude)) for log in gps_logs]
        gps_distance = calculate_distance(gps_coords)
    else:
        gps_distance = 0.0

    # Get activity data (last 6 hours before event)
    activity_window = event_time - timedelta(hours=6)
    activity_logs = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.logged_at >= activity_window,
        ActivityLog.logged_at <= event_time
    ).all()

    orders_completed = sum(log.orders_count for log in activity_logs) if activity_logs else 0
    is_online = any(log.status in ['online', 'delivering'] for log in activity_logs) if activity_logs else False

    return {
        'gps_distance': gps_distance,
        'orders_completed': orders_completed,
        'is_online': is_online
    }


def calculate_distance(coords):
    """Calculate total distance from GPS coordinates using Haversine formula"""
    if not coords or len(coords) < 2:
        return 0.0

    from math import radians, sin, cos, sqrt, atan2

    total_distance = 0.0
    R = 6371  # Earth's radius in km

    for i in range(1, len(coords)):
        lat1, lon1 = coords[i - 1]
        lat2, lon2 = coords[i]

        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        total_distance += R * c

    return total_distance


def get_payout_for_event(event_type):
    """
    Get payout amount for event type.

    Args:
        event_type (str): Type of event

    Returns:
        float: Payout amount in rupees
    """
    payouts = {
        'extreme_heat': 200,
        'heavy_rain': 200,
        'platform_outage': 150,
        'smog': 100,
        'blackout': 150
    }

    return payouts.get(event_type, 200)


def detect_fraud_clusters(event_id):
    """
    Detect fraud rings by clustering claims from same location.

    If multiple users claim from exact same location, flag as fraud ring.

    Args:
        event_id (str): Event ID

    Returns:
        list: User IDs flagged as potential fraud ring members
    """
    from collections import defaultdict

    # Get all claims for this event
    claims = Claim.query.filter_by(event_id=event_id).all()

    if len(claims) < 5:
        return []

    # Get GPS locations at claim time
    location_clusters = defaultdict(list)

    for claim in claims:
        # Get most recent GPS log
        gps_log = GPSLog.query.filter_by(user_id=claim.user_id).order_by(
            GPSLog.logged_at.desc()
        ).first()

        if gps_log:
            # Round to 3 decimal places (~100m precision)
            location_key = (round(float(gps_log.latitude), 3), round(float(gps_log.longitude), 3))
            location_clusters[location_key].append(claim.user_id)

    # Find clusters with >= 5 users
    fraud_ring_members = []
    for location, user_ids in location_clusters.items():
        if len(user_ids) >= 5:
            logger.warning(f"🚨 Fraud ring detected at {location}: {len(user_ids)} users")
            fraud_ring_members.extend(user_ids)

    return fraud_ring_members
