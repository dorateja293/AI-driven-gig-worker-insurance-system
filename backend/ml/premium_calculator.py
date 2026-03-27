"""
MODULE 1: Dynamic Premium Calculation (Risk Scoring)

Calculates insurance premium based on weather risk factors and zone data.
Simple, explainable ML for demo purposes.
"""

def calculate_premium(heat_days, rain_days, zone_risk, season_factor=1.0):
    """
    Calculate insurance premium using weighted risk scoring.

    Args:
        heat_days (int): Number of extreme heat days (0-30)
        rain_days (int): Number of heavy rain days (0-30)
        zone_risk (float): Zone risk factor (0-1)
        season_factor (float): Seasonal multiplier (0.8-1.5)

    Returns:
        dict: {
            "risk_score": float (0-1),
            "premium": int (rupees)
        }
    """
    # Normalize heat and rain days to 0-1 scale
    heat_norm = min(heat_days / 30.0, 1.0)
    rain_norm = min(rain_days / 30.0, 1.0)

    # Weighted risk score calculation
    # 40% heat, 40% rain, 20% zone risk
    risk_score = (
        0.4 * heat_norm +
        0.4 * rain_norm +
        0.2 * zone_risk
    )

    # Clamp risk score between 0 and 1
    risk_score = max(0.0, min(1.0, risk_score))

    # Base premium calculation
    base_rate = 30
    premium = base_rate * (1 + risk_score) * season_factor

    # Zone-based adjustments
    if zone_risk < 0.3:
        # Safe zone discount
        premium -= 2
    elif zone_risk > 0.7:
        # High-risk zone surcharge
        premium += 5

    # Round to integer
    premium = int(round(premium))

    # Ensure minimum premium
    premium = max(20, premium)

    return {
        "risk_score": round(risk_score, 3),
        "premium": premium,
        "breakdown": {
            "base_rate": base_rate,
            "heat_contribution": round(0.4 * heat_norm, 3),
            "rain_contribution": round(0.4 * rain_norm, 3),
            "zone_contribution": round(0.2 * zone_risk, 3),
            "season_multiplier": season_factor
        }
    }


def get_zone_risk_profile(zone_name):
    """
    Get predefined risk profile for a zone.
    In production, this would query historical weather data.
    """
    zone_profiles = {
        'Zone-A': {'heat_days': 12, 'rain_days': 8, 'zone_risk': 0.4},
        'Zone-B': {'heat_days': 18, 'rain_days': 15, 'zone_risk': 0.6},
        'Zone-C': {'heat_days': 8, 'rain_days': 5, 'zone_risk': 0.2},
        'Zone-D': {'heat_days': 22, 'rain_days': 20, 'zone_risk': 0.8},
    }

    return zone_profiles.get(zone_name, {'heat_days': 10, 'rain_days': 10, 'zone_risk': 0.5})


def calculate_premium_for_zone(zone_name, season_factor=1.0):
    """
    Convenience function to calculate premium using zone name.

    Args:
        zone_name (str): Zone identifier (e.g., 'Zone-A')
        season_factor (float): Seasonal multiplier

    Returns:
        dict: Premium calculation result
    """
    profile = get_zone_risk_profile(zone_name)

    return calculate_premium(
        heat_days=profile['heat_days'],
        rain_days=profile['rain_days'],
        zone_risk=profile['zone_risk'],
        season_factor=season_factor
    )


if __name__ == "__main__":
    # Test the premium calculator
    print("=== Premium Calculator Test ===\n")

    # Test 1: Low risk zone
    result = calculate_premium(heat_days=5, rain_days=3, zone_risk=0.2, season_factor=1.0)
    print(f"Low Risk Zone: {result}")

    # Test 2: High risk zone
    result = calculate_premium(heat_days=25, rain_days=20, zone_risk=0.8, season_factor=1.2)
    print(f"\nHigh Risk Zone: {result}")

    # Test 3: Using zone profiles
    for zone in ['Zone-A', 'Zone-B', 'Zone-C', 'Zone-D']:
        result = calculate_premium_for_zone(zone, season_factor=1.0)
        print(f"\n{zone}: Premium = ₹{result['premium']}, Risk Score = {result['risk_score']}")
