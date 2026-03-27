from datetime import datetime
from flask import current_app
from app import db
from app.models import Event, Policy, User, Claim
from app.services.fraud_detection import calculate_fraud_score, detect_fraud_clusters
from app.services.payout_service import execute_payout

def process_claim_for_event(event_id):
    """
    Process claims for a specific event
    1. Find all active policies in the event zone
    2. Run fraud detection for each eligible user
    3. Create claim records based on fraud score
    4. Execute payouts for auto-approved claims
    """
    try:
        # Get event
        event = Event.query.get(event_id)
        if not event:
            print(f"Event {event_id} not found")
            return

        print(f"Processing claims for event {event_id} in zone {event.zone}")

        # Get payout amount from config based on event type
        thresholds = current_app.config['THRESHOLDS']
        payout_amount = thresholds.get(event.event_type, {}).get('payout', 200)

        # Find all users with active policies in this zone
        today = datetime.utcnow().date()
        active_policies = Policy.query.join(User).filter(
            User.zone == event.zone,
            Policy.status == 'active',
            Policy.start_date <= today,
            Policy.end_date >= today
        ).all()

        print(f"Found {len(active_policies)} active policies in zone {event.zone}")

        if len(active_policies) == 0:
            return

        # First, create all claims
        claims_created = []
        for policy in active_policies:
            # Check if claim already exists for this user and event
            existing_claim = Claim.query.filter_by(
                user_id=policy.user_id,
                event_id=event_id
            ).first()

            if existing_claim:
                print(f"Claim already exists for user {policy.user_id}")
                continue

            # Calculate initial fraud score (layers 1-3)
            fraud_score, fraud_reasons = calculate_fraud_score(policy.user_id, event_id)

            # Create claim
            claim = Claim(
                user_id=policy.user_id,
                policy_id=policy.id,
                event_id=event_id,
                payout_amount=payout_amount,
                fraud_score=fraud_score,
                fraud_reason='; '.join(fraud_reasons) if fraud_reasons else None,
                status='pending'
            )
            db.session.add(claim)
            claims_created.append(claim)

        db.session.commit()
        print(f"Created {len(claims_created)} claims")

        # Now run cluster detection (Layer 4) on all claims for this event
        cluster_scores = detect_fraud_clusters(event_id)

        # Update fraud scores for users in clusters
        for user_id, cluster_data in cluster_scores.items():
            claim = next((c for c in claims_created if c.user_id == user_id), None)
            if not claim:
                # Get existing claim
                claim = Claim.query.filter_by(user_id=user_id, event_id=event_id).first()

            if claim:
                # Add cluster score to existing fraud score
                claim.fraud_score = min(claim.fraud_score + cluster_data['score'], 1.0)

                # Append cluster reasons
                existing_reasons = claim.fraud_reason.split('; ') if claim.fraud_reason else []
                existing_reasons.extend(cluster_data['reasons'])
                claim.fraud_reason = '; '.join(existing_reasons)

        db.session.commit()
        print(f"Updated fraud scores with cluster detection")

        # Process claims based on fraud score
        fraud_thresholds = current_app.config['FRAUD_THRESHOLDS']
        low_threshold = fraud_thresholds['low']
        medium_threshold = fraud_thresholds['medium']

        for claim in Claim.query.filter_by(event_id=event_id).all():
            if claim.fraud_score < low_threshold:
                # Auto-approve and payout immediately
                claim.status = 'approved'
                db.session.commit()

                # Execute payout
                result = execute_payout(claim.user_id, claim.id, claim.payout_amount)
                if result['success']:
                    print(f"Paid out claim {claim.id} to user {claim.user_id}")
                else:
                    print(f"Payout failed for claim {claim.id}: {result['error']}")

            elif claim.fraud_score < medium_threshold:
                # Delayed approval (for now, auto-approve but mark for review)
                claim.status = 'approved'
                db.session.commit()
                print(f"Claim {claim.id} approved with delay (medium risk)")

            else:
                # High/Critical - flag for manual review
                claim.status = 'flagged'
                db.session.commit()
                print(f"Claim {claim.id} flagged for review (high/critical risk)")

        print(f"Finished processing claims for event {event_id}")

    except Exception as e:
        db.session.rollback()
        print(f"Error processing claims for event {event_id}: {e}")
        raise
