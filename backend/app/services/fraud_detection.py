import numpy as np
from datetime import datetime, timedelta
from sklearn.cluster import DBSCAN
from app.models import GPSLog, ActivityLog, User, Event
from app import db

def calculate_fraud_score(user_id, event_id):
    """
    Multi-layer fraud detection pipeline
    Returns: (fraud_score, fraud_reasons[])
    """
    fraud_score = 0.0
    fraud_reasons = []

    # Get event details
    event = Event.query.get(event_id)
    if not event:
        return 0.0, []

    # Layer 1: GPS Consistency Check
    gps_score, gps_reasons = check_gps_consistency(user_id, event.detected_at)
    fraud_score += gps_score
    fraud_reasons.extend(gps_reasons)

    # Layer 2: Activity Validation
    activity_score, activity_reasons = check_activity_validation(user_id, event.detected_at)
    fraud_score += activity_score
    fraud_reasons.extend(activity_reasons)

    # Layer 3: Movement Pattern Analysis
    movement_score, movement_reasons = check_movement_patterns(user_id, event.detected_at)
    fraud_score += movement_score
    fraud_reasons.extend(movement_reasons)

    # Ensure score doesn't exceed 1.0 at this point
    fraud_score = min(fraud_score, 1.0)

    return round(fraud_score, 2), fraud_reasons


def check_gps_consistency(user_id, event_time):
    """
    Layer 1: GPS Consistency Check
    - Check for sudden coordinate jumps
    - Check for exact same coordinates (spoofing indicator)
    """
    score = 0.0
    reasons = []

    # Get GPS logs from last 4 hours before event
    time_window_start = event_time - timedelta(hours=4)
    gps_logs = GPSLog.query.filter(
        GPSLog.user_id == user_id,
        GPSLog.logged_at >= time_window_start,
        GPSLog.logged_at <= event_time
    ).order_by(GPSLog.logged_at).all()

    if len(gps_logs) == 0:
        # No GPS data - medium suspicion
        score += 0.2
        reasons.append('No GPS data in last 4 hours')
        return score, reasons

    if len(gps_logs) < 3:
        # Very few GPS points - slightly suspicious
        score += 0.1
        reasons.append('Insufficient GPS history')
        return score, reasons

    # Check for exact duplicate coordinates (spoofing indicator)
    coords = [(float(log.latitude), float(log.longitude)) for log in gps_logs]
    unique_coords = set(coords)

    if len(unique_coords) == 1 and len(gps_logs) > 5:
        # Same exact coordinates for extended period
        score += 0.3
        reasons.append('Static GPS position (exact duplicate coordinates)')

    # Check for sudden jumps (teleportation)
    for i in range(1, len(gps_logs)):
        prev_log = gps_logs[i-1]
        curr_log = gps_logs[i]

        # Calculate distance in km
        distance = haversine_distance(
            float(prev_log.latitude), float(prev_log.longitude),
            float(curr_log.latitude), float(curr_log.longitude)
        )

        # Calculate time difference in hours
        time_diff = (curr_log.logged_at - prev_log.logged_at).total_seconds() / 3600

        if time_diff > 0:
            speed = distance / time_diff  # km/h

            # Impossible speed (> 200 km/h)
            if speed > 200:
                score += 0.3
                reasons.append(f'Impossible movement speed: {speed:.1f} km/h')
                break

    return score, reasons


def check_activity_validation(user_id, event_time):
    """
    Layer 2: Activity Validation
    - Check platform activity before the event
    - Check order count and online status
    """
    score = 0.0
    reasons = []

    # Get activity logs from last 6 hours before event
    time_window_start = event_time - timedelta(hours=6)
    activity_logs = ActivityLog.query.filter(
        ActivityLog.user_id == user_id,
        ActivityLog.logged_at >= time_window_start,
        ActivityLog.logged_at <= event_time
    ).order_by(ActivityLog.logged_at.desc()).all()

    if len(activity_logs) == 0:
        # No activity data - high suspicion
        score += 0.3
        reasons.append('No platform activity in last 6 hours')
        return score, reasons

    # Check if user was offline all day but suddenly claiming
    recent_activity = activity_logs[0]
    if recent_activity.status == 'offline':
        # Check if there's any online activity in the window
        online_count = sum(1 for log in activity_logs if log.status in ['online', 'delivering'])

        if online_count == 0:
            score += 0.4
            reasons.append('User was offline entire period before event')

    # Check order count
    total_orders = sum(log.orders_count for log in activity_logs)
    if total_orders == 0:
        score += 0.2
        reasons.append('Zero orders before event')

    return score, reasons


def check_movement_patterns(user_id, event_time):
    """
    Layer 3: Movement Pattern Analysis
    - Check speed consistency
    - Check distance traveled
    """
    score = 0.0
    reasons = []

    # Get GPS logs from last 2 hours
    time_window_start = event_time - timedelta(hours=2)
    gps_logs = GPSLog.query.filter(
        GPSLog.user_id == user_id,
        GPSLog.logged_at >= time_window_start,
        GPSLog.logged_at <= event_time
    ).order_by(GPSLog.logged_at).all()

    if len(gps_logs) < 2:
        return score, reasons

    # Check if speed is consistently 0 (static)
    speeds = [float(log.speed_kmh) for log in gps_logs]
    avg_speed = sum(speeds) / len(speeds)

    if avg_speed == 0 and len(gps_logs) > 5:
        score += 0.2
        reasons.append('Zero movement (static position)')

    # Calculate total distance traveled
    total_distance = 0
    for i in range(1, len(gps_logs)):
        prev_log = gps_logs[i-1]
        curr_log = gps_logs[i]

        distance = haversine_distance(
            float(prev_log.latitude), float(prev_log.longitude),
            float(curr_log.latitude), float(curr_log.longitude)
        )
        total_distance += distance

    # Delivery workers should travel 5-30 km in 2 hours
    if total_distance < 1:
        score += 0.1
        reasons.append(f'Minimal distance traveled: {total_distance:.2f} km')

    return score, reasons


def detect_fraud_clusters(event_id):
    """
    Layer 4: Cluster Detection (Fraud Ring Detection)
    Use DBSCAN to detect coordinated GPS spoofing attacks
    Returns: dict mapping user_id to cluster score and reasons
    """
    fraud_cluster_scores = {}

    # Get all claims for this event
    from app.models import Claim
    claims = Claim.query.filter_by(event_id=event_id).all()

    if len(claims) < 5:
        # Not enough claims to form a cluster
        return fraud_cluster_scores

    # Get the most recent GPS coordinate for each claimant at event time
    event = Event.query.get(event_id)
    claimant_coords = []
    claimant_users = []

    for claim in claims:
        # Get most recent GPS log before event
        gps_log = GPSLog.query.filter(
            GPSLog.user_id == claim.user_id,
            GPSLog.logged_at <= event.detected_at
        ).order_by(GPSLog.logged_at.desc()).first()

        if gps_log:
            claimant_coords.append([float(gps_log.latitude), float(gps_log.longitude)])
            claimant_users.append(claim.user_id)

    if len(claimant_coords) < 5:
        return fraud_cluster_scores

    # Run DBSCAN clustering
    # eps = 0.0005 degrees ≈ 50 meters
    # min_samples = 5 (at least 5 users in same location)
    coords_array = np.array(claimant_coords)
    clustering = DBSCAN(eps=0.0005, min_samples=5, metric='euclidean').fit(coords_array)

    labels = clustering.labels_

    # Identify fraud ring clusters (label != -1 means part of a cluster)
    cluster_ids = set(labels)
    cluster_ids.discard(-1)  # Remove noise points

    for cluster_id in cluster_ids:
        # Get all users in this cluster
        cluster_user_indices = [i for i, label in enumerate(labels) if label == cluster_id]

        if len(cluster_user_indices) >= 5:
            # This is a potential fraud ring
            for idx in cluster_user_indices:
                user_id = claimant_users[idx]

                # Add 0.6 to fraud score for being in a cluster
                cluster_score = 0.6
                cluster_reasons = [f'Part of GPS cluster with {len(cluster_user_indices)} users at same location']

                # Additional checks for this cluster
                # Check if these users also have zero activity
                activity_check = check_cluster_activity(claimant_users[cluster_user_indices], event.detected_at)

                if activity_check['zero_activity_count'] > len(cluster_user_indices) * 0.7:
                    # More than 70% have zero activity
                    cluster_score += 0.2
                    cluster_reasons.append('Cluster has coordinated zero activity')

                fraud_cluster_scores[user_id] = {
                    'score': cluster_score,
                    'reasons': cluster_reasons
                }

    return fraud_cluster_scores


def check_cluster_activity(user_ids, event_time):
    """Check activity patterns for a cluster of users"""
    time_window_start = event_time - timedelta(hours=6)

    zero_activity_count = 0

    for user_id in user_ids:
        activity_logs = ActivityLog.query.filter(
            ActivityLog.user_id == user_id,
            ActivityLog.logged_at >= time_window_start,
            ActivityLog.logged_at <= event_time
        ).all()

        total_orders = sum(log.orders_count for log in activity_logs)
        if total_orders == 0:
            zero_activity_count += 1

    return {
        'zero_activity_count': zero_activity_count,
        'total_users': len(user_ids)
    }


def haversine_distance(lat1, lon1, lat2, lon2):
    """
    Calculate distance between two GPS coordinates using Haversine formula
    Returns distance in kilometers
    """
    from math import radians, sin, cos, sqrt, atan2

    R = 6371  # Earth's radius in kilometers

    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))

    distance = R * c
    return distance
