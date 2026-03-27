"""
MODULE 2: Fraud Detection (Anomaly Detection)

Detects fraudulent insurance claims using rule-based anomaly detection.
Simple, explainable scoring for demo purposes.
"""

from datetime import datetime, timedelta


def detect_fraud(
    gps_movement,
    orders_completed,
    is_online,
    claim_time,
    event_time,
    nearby_claims_count
):
    """
    Detect potential fraud in insurance claims using anomaly detection.

    Args:
        gps_movement (list or float): List of GPS coordinates or total distance moved (km)
        orders_completed (int): Number of orders completed before event
        is_online (bool): Whether user was online during event
        claim_time (datetime or str): When claim was submitted
        event_time (datetime or str): When disruption event occurred
        nearby_claims_count (int): Number of claims from nearby workers

    Returns:
        dict: {
            "fraud_score": float (0-1),
            "risk_level": str ("LOW" | "MEDIUM" | "HIGH"),
            "action": str ("APPROVE" | "REVIEW" | "FLAG"),
            "reasons": list of str
        }
    """
    fraud_score = 0.0
    reasons = []

    # Convert timestamps to datetime if needed
    if isinstance(claim_time, str):
        claim_time = datetime.fromisoformat(claim_time.replace('Z', '+00:00'))
    if isinstance(event_time, str):
        event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00'))

    # Rule 1: No orders completed before event
    if orders_completed == 0:
        fraud_score += 0.3
        reasons.append("No orders completed before event")

    # Rule 2: GPS static (no movement)
    if isinstance(gps_movement, list):
        # Calculate total distance from list of coordinates
        total_distance = calculate_total_distance(gps_movement)
    else:
        # Assume gps_movement is already a distance value
        total_distance = gps_movement

    if total_distance < 0.5:  # Less than 500 meters
        fraud_score += 0.3
        reasons.append("GPS shows static position (minimal movement)")

    # Rule 3: Instant claim after event (within 5 minutes)
    time_diff = abs((claim_time - event_time).total_seconds() / 60)
    if time_diff < 5:
        fraud_score += 0.1
        reasons.append("Claim submitted instantly after event")

    # Rule 4: User was offline during event
    if not is_online:
        fraud_score += 0.2
        reasons.append("User was offline during event period")

    # Rule 5: Suspicious cluster (many nearby claims)
    if nearby_claims_count > 50:
        fraud_score += 0.4
        reasons.append(f"High nearby claims ({nearby_claims_count}) - potential fraud ring")
    elif nearby_claims_count > 20:
        fraud_score += 0.2
        reasons.append(f"Moderate nearby claims ({nearby_claims_count})")

    # Clamp fraud score between 0 and 1
    fraud_score = max(0.0, min(1.0, fraud_score))

    # Determine risk level and action
    if fraud_score < 0.3:
        risk_level = "LOW"
        action = "APPROVE"
    elif fraud_score < 0.7:
        risk_level = "MEDIUM"
        action = "REVIEW"
    else:
        risk_level = "HIGH"
        action = "FLAG"

    return {
        "fraud_score": round(fraud_score, 3),
        "risk_level": risk_level,
        "action": action,
        "reasons": reasons,
        "details": {
            "orders_completed": orders_completed,
            "gps_distance_km": round(total_distance, 2),
            "time_to_claim_minutes": round(time_diff, 1),
            "nearby_claims": nearby_claims_count,
            "was_online": is_online
        }
    }


def calculate_total_distance(gps_coordinates):
    """
    Calculate total distance traveled from list of GPS coordinates.

    Args:
        gps_coordinates (list): List of (lat, lon) tuples

    Returns:
        float: Total distance in kilometers
    """
    if not gps_coordinates or len(gps_coordinates) < 2:
        return 0.0

    from math import radians, sin, cos, sqrt, atan2

    total_distance = 0.0
    R = 6371  # Earth's radius in kilometers

    for i in range(1, len(gps_coordinates)):
        lat1, lon1 = gps_coordinates[i - 1]
        lat2, lon2 = gps_coordinates[i]

        # Haversine formula
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        total_distance += R * c

    return total_distance


def detect_fraud_batch(claims_data):
    """
    Process multiple claims for fraud detection.

    Args:
        claims_data (list): List of claim dictionaries

    Returns:
        list: Fraud detection results for each claim
    """
    results = []

    for claim in claims_data:
        result = detect_fraud(
            gps_movement=claim.get('gps_movement', 0),
            orders_completed=claim.get('orders_completed', 0),
            is_online=claim.get('is_online', True),
            claim_time=claim.get('claim_time', datetime.utcnow()),
            event_time=claim.get('event_time', datetime.utcnow()),
            nearby_claims_count=claim.get('nearby_claims_count', 0)
        )

        results.append({
            'claim_id': claim.get('claim_id'),
            'fraud_analysis': result
        })

    return results


if __name__ == "__main__":
    # Test the fraud detector
    print("=== Fraud Detector Test ===\n")

    # Test 1: Legitimate claim
    result = detect_fraud(
        gps_movement=15.5,  # 15.5 km traveled
        orders_completed=12,
        is_online=True,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(hours=1),
        nearby_claims_count=5
    )
    print(f"Legitimate Claim: {result}")

    # Test 2: Suspicious claim
    result = detect_fraud(
        gps_movement=0.2,  # Almost no movement
        orders_completed=0,
        is_online=False,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(minutes=2),
        nearby_claims_count=60
    )
    print(f"\nSuspicious Claim: {result}")

    # Test 3: Medium risk claim
    result = detect_fraud(
        gps_movement=3.0,
        orders_completed=2,
        is_online=True,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(minutes=3),
        nearby_claims_count=25
    )
    print(f"\nMedium Risk Claim: {result}")
