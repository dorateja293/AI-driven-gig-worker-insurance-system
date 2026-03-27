from flask import current_app

def calculate_premium(zone, city):
    """
    Calculate dynamic premium based on zone risk profile

    Formula:
      risk_score = (0.3 * rain_freq_norm) + (0.3 * heat_days_norm)
                 + (0.2 * zone_risk) + (0.2 * seasonal_factor_norm)
      premium = BASE_RATE * (1 + risk_score)

    Returns: {risk_score, premium}
    """
    # Get zone risk profile from config
    zone_profiles = current_app.config['ZONE_RISK_PROFILES']

    if zone not in zone_profiles:
        # Default to Zone-A if zone not found
        zone = 'Zone-A'

    profile = zone_profiles[zone]

    # Normalize values (0-1 scale)
    rain_freq_norm = min(profile['rain_frequency'] / 30, 1.0)  # Max 30 days/month
    heat_days_norm = min(profile['heat_days'] / 30, 1.0)       # Max 30 days/month
    zone_risk = profile['zone_risk']                           # Already 0-1
    seasonal_factor_norm = min((profile['seasonal_factor'] - 0.8) / 0.7, 1.0)  # Normalize from 0.8-1.5 to 0-1

    # Calculate weighted risk score
    risk_score = (
        0.3 * rain_freq_norm +
        0.3 * heat_days_norm +
        0.2 * zone_risk +
        0.2 * seasonal_factor_norm
    )

    # Ensure risk_score is between 0 and 1
    risk_score = max(0.0, min(1.0, risk_score))

    # Calculate premium
    base_rate = current_app.config['BASE_PREMIUM']
    
    # Hackathon Feature: Dynamic pricing models (₹2 less if safe from water logging)
    water_logging_safe_discount = 2.0 if zone_risk <= 0.3 else 0.0
    
    premium = (base_rate * (1 + risk_score)) - water_logging_safe_discount

    return {
        'risk_score': round(risk_score, 2),
        'premium': round(premium, 2)
    }


def get_coverage_triggers():
    """Get list of coverage triggers based on thresholds"""
    triggers = []
    thresholds = current_app.config['THRESHOLDS']

    for event_type in thresholds:
        triggers.append(event_type)

    return triggers


def get_max_payout():
    """Get maximum payout amount across all event types"""
    thresholds = current_app.config['THRESHOLDS']
    max_payout = max(threshold['payout'] for threshold in thresholds.values())
    return max_payout
