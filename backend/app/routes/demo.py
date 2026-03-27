"""
Demo Routes - 2-Minute Demo Flow

THE MOST IMPORTANT ENDPOINT: /demo/run

This endpoint simulates the complete insurance flow for hackathon demos:
Register → Buy Policy → Trigger Event → Auto Claim → Instant Payout

Perfect for narrating: "Watch what happens when extreme heat strikes..."
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
from app import db
from app.models import User, Policy, Wallet, WalletTransaction, GPSLog, ActivityLog
from app.services.event_simulator import trigger_event, trigger_preset_demo, get_event_statistics
from ml.premium_calculator import calculate_premium_for_zone
import random
import logging

bp = Blueprint('demo', __name__, url_prefix='/api/demo')
logger = logging.getLogger(__name__)


@bp.route('/run', methods=['POST'])
def run_demo():
    """
    🎬 THE KILLER DEMO ENDPOINT

    Runs complete insurance flow in one API call:
    1. Register worker (or use existing)
    2. Top up wallet & buy policy
    3. Trigger disruption event
    4. Auto-process claims with fraud detection
    5. Execute instant payouts

    Request: {
        "worker_name": "Ravi Kumar" (optional),
        "zone": "Zone-D" (optional),
        "event_type": "HEAT" (optional: HEAT, RAIN, OUTAGE, SMOG, BLACKOUT)
    }

    Response: {
        "demo_summary": "narrative-ready summary",
        "worker": {...},
        "policy": {...},
        "event": {...},
        "claim_automation": {...},
        "final_wallet_balance": float
    }
    """
    try:
        data = request.get_json() or {}

        worker_name = data.get('worker_name', f'Demo Worker {random.randint(100, 999)}')
        zone = data.get('zone', 'Zone-D')
        event_type = data.get('event_type', 'HEAT')

        logger.info(f"🎬 Starting demo flow for {worker_name} in {zone}")

        # Step 1: Register worker (or get existing)
        logger.info("📝 Step 1: Registering worker...")

        phone = f"98765{random.randint(10000, 99999)}"
        user = User(
            name=worker_name,
            phone=phone,
            city='Hyderabad' if zone.endswith('D') else 'Mumbai',
            zone=zone,
            platform='Swiggy'
        )
        db.session.add(user)
        db.session.flush()

        # Create wallet
        wallet = Wallet(user_id=user.id, balance=0)
        db.session.add(wallet)
        db.session.flush()

        # Create mock GPS and activity logs for realistic fraud detection
        create_mock_activity_logs(user.id)

        db.session.commit()

        logger.info(f"✅ Worker registered: {user.name} ({user.id})")

        # Step 2: Top up wallet and buy policy
        logger.info("💰 Step 2: Funding wallet and purchasing policy...")

        # Top up ₹100
        wallet.balance = 100
        top_up_txn = WalletTransaction(
            wallet_id=wallet.id,
            type='top_up',
            amount=100,
            description='Demo wallet funding'
        )
        db.session.add(top_up_txn)

        # Calculate premium
        premium_data = calculate_premium_for_zone(zone, season_factor=1.2)
        premium = premium_data['premium']

        # Debit premium
        wallet.balance -= premium
        premium_txn = WalletTransaction(
            wallet_id=wallet.id,
            type='premium_paid',
            amount=-premium,
            description=f'Insurance premium - {zone}'
        )
        db.session.add(premium_txn)

        # Create policy
        today = datetime.utcnow().date()
        policy = Policy(
            user_id=user.id,
            risk_score=premium_data['risk_score'],
            premium=premium,
            start_date=today,
            end_date=today + timedelta(days=7),
            status='active'
        )
        db.session.add(policy)

        db.session.commit()

        logger.info(f"✅ Policy purchased: ₹{premium} premium, 7 days coverage")

        balance_after_premium = float(wallet.balance)

        # Step 3: Trigger event and auto-process claims
        logger.info(f"⚡ Step 3: Triggering {event_type} event in {zone}...")

        event_result = trigger_event(
            event_type=event_type,
            zone=zone
        )

        logger.info(f"✅ Event triggered: {event_result['event']['event_id']}")

        # Get updated wallet balance
        db.session.refresh(wallet)
        final_balance = float(wallet.balance)

        # Find the claim that was created for this user
        from app.models import Claim
        user_claim = Claim.query.filter_by(
            user_id=user.id,
            event_id=event_result['event']['event_id']
        ).first()

        # Generate demo-ready summary
        demo_summary = generate_demo_narrative(
            worker_name=user.name,
            zone=zone,
            event_type=event_type,
            premium=premium,
            claim_status=user_claim.status if user_claim else 'not_created',
            payout=float(user_claim.payout_amount) if user_claim and user_claim.status == 'paid' else 0,
            fraud_score=float(user_claim.fraud_score) if user_claim else 0,
            total_claims=event_result['automation']['eligible_workers'],
            approved_claims=event_result['automation']['approved'],
            total_payout=event_result['automation']['total_payout']
        )

        logger.info(f"🎉 Demo complete: {demo_summary}")

        # Return complete demo results
        return jsonify({
            'demo_summary': demo_summary,
            'narration': {
                'step_1': f"✅ {user.name} registered in {zone}",
                'step_2': f"✅ Purchased ₹{premium} policy (risk: {premium_data['risk_score']})",
                'step_3': f"⚡ {event_result['summary']}",
                'step_4': f"💰 Final balance: ₹{final_balance:.2f}"
            },
            'worker': {
                'user_id': user.id,
                'name': user.name,
                'phone': user.phone,
                'zone': user.zone,
                'platform': user.platform
            },
            'policy': {
                'policy_id': policy.id,
                'risk_score': float(policy.risk_score),
                'premium': float(policy.premium),
                'coverage_days': 7,
                'status': policy.status
            },
            'wallet': {
                'initial_balance': 100.0,
                'after_premium': balance_after_premium,
                'final_balance': final_balance,
                'net_gain': final_balance - balance_after_premium
            },
            'event': event_result['event'],
            'claim_automation': event_result['automation'],
            'user_claim': {
                'claim_id': user_claim.id if user_claim else None,
                'status': user_claim.status if user_claim else 'not_created',
                'payout_amount': float(user_claim.payout_amount) if user_claim else 0,
                'fraud_score': float(user_claim.fraud_score) if user_claim else 0,
                'risk_level': user_claim.risk_level if user_claim else None
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        logger.error(f"❌ Demo failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@bp.route('/trigger-event', methods=['POST'])
def trigger_demo_event():
    """
    Trigger a single event for testing.

    Request: {
        "event_type": "HEAT",
        "zone": "Zone-D"
    }

    Response: Event and claim automation results
    """
    try:
        data = request.get_json()

        event_type = data.get('event_type', 'HEAT')
        zone = data.get('zone', 'Zone-D')

        logger.info(f"⚡ Triggering {event_type} event in {zone}")

        result = trigger_event(event_type=event_type, zone=zone)

        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Error triggering event: {str(e)}")
        return jsonify({'error': str(e)}), 500


@bp.route('/stats', methods=['GET'])
def get_demo_stats():
    """
    Get overall statistics for demo purposes.

    Response: System-wide statistics
    """
    try:
        zone = request.args.get('zone')

        stats = get_event_statistics(zone=zone)

        return jsonify(stats), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/reset', methods=['POST'])
def reset_demo():
    """
    Reset demo data (for clean demos).

    WARNING: Deletes all claims, events, and demo users.
    """
    try:
        from app.models import Claim, Event, User, Policy, Wallet

        # Delete all claims
        Claim.query.delete()

        # Delete all events
        Event.query.delete()

        # Optional: Delete demo users (be careful!)
        # User.query.filter(User.phone.like('98765%')).delete()

        db.session.commit()

        logger.info("🔄 Demo data reset successfully")

        return jsonify({'message': 'Demo reset complete'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


def generate_demo_narrative(worker_name, zone, event_type, premium, claim_status, payout, fraud_score, total_claims, approved_claims, total_payout):
    """
    Generate a narrative-ready summary for easy demo presentation.

    Returns:
        str: Narrative summary
    """
    event_names = {
        'HEAT': 'Extreme heat wave',
        'RAIN': 'Heavy rainfall',
        'OUTAGE': 'Platform outage',
        'SMOG': 'Severe smog',
        'BLACKOUT': 'Power blackout'
    }

    event_name = event_names.get(event_type.upper(), event_type)

    if claim_status == 'paid':
        narrative = (
            f"{event_name} strikes {zone}! "
            f"{worker_name} paid ₹{premium} premium. "
            f"Auto-claim processed: {total_claims} workers affected, "
            f"{approved_claims} approved, ₹{int(total_payout)} paid out. "
            f"{worker_name} received ₹{int(payout)} instantly (fraud score: {fraud_score:.2f})."
        )
    elif claim_status == 'flagged':
        narrative = (
            f"{event_name} strikes {zone}! "
            f"{worker_name}'s claim flagged due to suspicious activity (fraud score: {fraud_score:.2f}). "
            f"{total_claims} workers affected, {approved_claims} approved."
        )
    else:
        narrative = (
            f"{event_name} strikes {zone}! "
            f"{total_claims} workers affected, {approved_claims} claims auto-processed."
        )

    return narrative


def create_mock_activity_logs(user_id):
    """
    Create realistic activity logs for fraud detection.

    Makes the worker look legitimate with GPS movement and orders.
    """
    now = datetime.utcnow()

    # Create GPS logs (showing movement)
    base_lat = 17.385044  # Hyderabad
    base_lon = 78.486671

    for i in range(10):
        gps_log = GPSLog(
            user_id=user_id,
            latitude=base_lat + (random.random() - 0.5) * 0.05,  # ~5km variation
            longitude=base_lon + (random.random() - 0.5) * 0.05,
            speed_kmh=random.uniform(10, 30),
            logged_at=now - timedelta(hours=i)
        )
        db.session.add(gps_log)

    # Create activity logs (showing orders)
    for i in range(5):
        activity_log = ActivityLog(
            user_id=user_id,
            status='delivering' if i % 2 == 0 else 'online',
            orders_count=random.randint(2, 5),
            logged_at=now - timedelta(hours=i * 2)
        )
        db.session.add(activity_log)
