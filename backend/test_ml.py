"""
ML Modules Test Suite

Run this to test all 3 ML modules independently.

Usage:
    python test_ml.py
"""

import sys
import os

# Add ml directory to path
backend_path = os.path.dirname(os.path.abspath(__file__))
ml_path = os.path.join(backend_path, 'ml')
sys.path.insert(0, backend_path)
sys.path.insert(0, ml_path)

from ml.premium_calculator import calculate_premium, calculate_premium_for_zone
from ml.fraud_detector import detect_fraud
from ml.predictor import predict_disruption, get_insurance_urgency
from datetime import datetime, timedelta


def test_premium_calculator():
    """Test Module 1: Premium Calculator"""
    print("=" * 60)
    print("MODULE 1: PREMIUM CALCULATOR TESTS")
    print("=" * 60)

    # Test 1: Low Risk Zone
    print("\n[Test 1] Low Risk Zone (Zone-C)")
    result = calculate_premium_for_zone('Zone-C', season_factor=1.0)
    print(f"  Risk Score: {result['risk_score']}")
    print(f"  Premium: ₹{result['premium']}")
    print(f"  Breakdown: {result['breakdown']}")
    assert result['premium'] < 40, "Low risk zone should have lower premium"

    # Test 2: High Risk Zone
    print("\n[Test 2] High Risk Zone (Zone-D)")
    result = calculate_premium_for_zone('Zone-D', season_factor=1.2)
    print(f"  Risk Score: {result['risk_score']}")
    print(f"  Premium: ₹{result['premium']}")
    print(f"  Breakdown: {result['breakdown']}")
    assert result['premium'] > 50, "High risk zone should have higher premium"

    # Test 3: Custom Parameters
    print("\n[Test 3] Custom Parameters")
    result = calculate_premium(
        heat_days=20,
        rain_days=15,
        zone_risk=0.6,
        season_factor=1.1
    )
    print(f"  Risk Score: {result['risk_score']}")
    print(f"  Premium: ₹{result['premium']}")

    # Test 4: All Zones Comparison
    print("\n[Test 4] All Zones Comparison")
    for zone in ['Zone-A', 'Zone-B', 'Zone-C', 'Zone-D']:
        result = calculate_premium_for_zone(zone)
        print(f"  {zone}: ₹{result['premium']:>3} | Risk: {result['risk_score']}")

    print("\n✅ Premium Calculator Tests Passed!")


def test_fraud_detector():
    """Test Module 2: Fraud Detector"""
    print("\n" + "=" * 60)
    print("MODULE 2: FRAUD DETECTOR TESTS")
    print("=" * 60)

    # Test 1: Legitimate Claim
    print("\n[Test 1] Legitimate Claim")
    result = detect_fraud(
        gps_movement=15.5,
        orders_completed=12,
        is_online=True,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(hours=1),
        nearby_claims_count=5
    )
    print(f"  Fraud Score: {result['fraud_score']}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Action: {result['action']}")
    print(f"  Reasons: {result['reasons']}")
    assert result['action'] == 'APPROVE', "Legitimate claim should be approved"

    # Test 2: Highly Suspicious Claim
    print("\n[Test 2] Highly Suspicious Claim (Fraud Ring)")
    result = detect_fraud(
        gps_movement=0.1,
        orders_completed=0,
        is_online=False,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(minutes=2),
        nearby_claims_count=75
    )
    print(f"  Fraud Score: {result['fraud_score']}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Action: {result['action']}")
    print(f"  Reasons: {result['reasons']}")
    assert result['action'] == 'FLAG', "Fraudulent claim should be flagged"

    # Test 3: Medium Risk Claim
    print("\n[Test 3] Medium Risk Claim")
    result = detect_fraud(
        gps_movement=3.0,
        orders_completed=2,
        is_online=True,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(minutes=3),
        nearby_claims_count=25
    )
    print(f"  Fraud Score: {result['fraud_score']}")
    print(f"  Risk Level: {result['risk_level']}")
    print(f"  Action: {result['action']}")
    print(f"  Reasons: {result['reasons']}")
    assert result['action'] == 'REVIEW', "Medium risk should require review"

    # Test 4: GPS Coordinates Test
    print("\n[Test 4] GPS Coordinates Movement")
    gps_coords = [
        (17.385044, 78.486671),  # Hyderabad
        (17.395044, 78.496671),
        (17.405044, 78.506671),
        (17.415044, 78.516671)
    ]
    result = detect_fraud(
        gps_movement=gps_coords,
        orders_completed=8,
        is_online=True,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(hours=2),
        nearby_claims_count=10
    )
    print(f"  GPS Distance: {result['details']['gps_distance_km']} km")
    print(f"  Fraud Score: {result['fraud_score']}")
    print(f"  Action: {result['action']}")

    print("\n✅ Fraud Detector Tests Passed!")


def test_predictor():
    """Test Module 3: Disruption Predictor"""
    print("\n" + "=" * 60)
    print("MODULE 3: DISRUPTION PREDICTOR TESTS")
    print("=" * 60)

    # Test 1: High Heat Risk
    print("\n[Test 1] High Heat Risk")
    result = predict_disruption({
        "temperatures": [41, 42, 43, 44, 45, 44, 43],
        "rainfall": [0, 0, 2, 1, 0, 0, 3]
    })
    print(f"  Heat Risk: {result['heat_risk']}")
    print(f"  Rain Risk: {result['rain_risk']}")
    print(f"  Overall Risk: {result['overall_risk']}")
    print(f"  Recommendation: {result['recommendation']}")
    print(f"  Message: {result['message']}")
    assert result['recommendation'] in ['BUY_POLICY', 'CONSIDER_POLICY'], "High heat should recommend insurance"

    # Test 2: High Rain Risk
    print("\n[Test 2] High Rain Risk")
    result = predict_disruption({
        "temperatures": [32, 33, 31, 30, 32, 33, 31],
        "rainfall": [45, 52, 60, 48, 55, 50, 58]
    })
    print(f"  Heat Risk: {result['heat_risk']}")
    print(f"  Rain Risk: {result['rain_risk']}")
    print(f"  Overall Risk: {result['overall_risk']}")
    print(f"  Recommendation: {result['recommendation']}")
    assert result['recommendation'] in ['BUY_POLICY', 'CONSIDER_POLICY'], "High rain should recommend insurance"

    # Test 3: Safe Conditions
    print("\n[Test 3] Safe Conditions")
    result = predict_disruption({
        "temperatures": [28, 29, 30, 29, 28, 30, 29],
        "rainfall": [5, 8, 3, 0, 2, 6, 4]
    })
    print(f"  Heat Risk: {result['heat_risk']}")
    print(f"  Rain Risk: {result['rain_risk']}")
    print(f"  Overall Risk: {result['overall_risk']}")
    print(f"  Recommendation: {result['recommendation']}")
    assert result['recommendation'] == 'SAFE', "Safe conditions should not recommend insurance"

    # Test 4: Insurance Urgency Score
    print("\n[Test 4] Insurance Urgency Scoring")
    result = get_insurance_urgency({
        "temperatures": [42, 43, 44, 45, 46, 45, 44],
        "rainfall": [0, 0, 0, 0, 0, 0, 0]
    })
    print(f"  Urgency Score: {result['urgency_score']}/10")
    print(f"  Urgency Level: {result['urgency_level']}")
    print(f"  Action: {result['action']}")

    print("\n✅ Disruption Predictor Tests Passed!")


def run_full_scenario_test():
    """Test a complete workflow scenario"""
    print("\n" + "=" * 60)
    print("COMPLETE SCENARIO: Worker Journey")
    print("=" * 60)

    # Scenario: Ravi the Delivery Worker
    print("\n📱 Ravi is a Swiggy delivery partner in Zone-D (high-risk zone)")

    # Step 1: Get premium quote
    print("\n[Step 1] Checking insurance premium...")
    premium_result = calculate_premium_for_zone('Zone-D', season_factor=1.2)
    print(f"  Premium Quote: ₹{premium_result['premium']}")
    print(f"  Risk Score: {premium_result['risk_score']}")

    # Step 2: Check weather forecast
    print("\n[Step 2] Checking next 7 days weather...")
    weather_data = {
        "temperatures": [42, 43, 44, 45, 46, 45, 44],
        "rainfall": [0, 0, 0, 0, 0, 0, 0]
    }
    prediction = predict_disruption(weather_data)
    print(f"  Heat Risk: {prediction['heat_risk']}")
    print(f"  Recommendation: {prediction['recommendation']}")
    print(f"  Message: {prediction['message']}")

    # Step 3: Ravi purchases insurance
    print("\n[Step 3] Ravi purchases insurance ✅")

    # Step 4: Extreme heat event occurs
    print("\n[Step 4] 🔥 Extreme heat event detected (45°C for 2.5 hours)")

    # Step 5: Automatic claim processing
    print("\n[Step 5] Processing auto-claim with fraud detection...")
    fraud_check = detect_fraud(
        gps_movement=12.5,  # Ravi was actively delivering
        orders_completed=8,
        is_online=True,
        claim_time=datetime.utcnow(),
        event_time=datetime.utcnow() - timedelta(hours=1),
        nearby_claims_count=15
    )
    print(f"  Fraud Score: {fraud_check['fraud_score']}")
    print(f"  Risk Level: {fraud_check['risk_level']}")
    print(f"  Action: {fraud_check['action']}")

    if fraud_check['action'] == 'APPROVE':
        print("\n[Step 6] ✅ Claim APPROVED - ₹200 credited to wallet instantly!")
    elif fraud_check['action'] == 'REVIEW':
        print("\n[Step 6] ⏳ Claim under REVIEW - Manual verification needed")
    else:
        print("\n[Step 6] ⚠️  Claim FLAGGED - Possible fraud detected")

    print("\n✅ Complete Scenario Test Passed!")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("InsureX ML Modules - Test Suite")
    print("=" * 60)

    try:
        # Run all tests
        test_premium_calculator()
        test_fraud_detector()
        test_predictor()
        run_full_scenario_test()

        print("\n" + "=" * 60)
        print("🎉 ALL TESTS PASSED SUCCESSFULLY!")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ Test Failed: {e}")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
