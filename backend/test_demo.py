"""
Demo Test Script

Quick script to test the /demo/run endpoint.

Usage:
    python test_demo.py
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"


def test_demo_flow():
    """Test the complete demo flow"""
    print("=" * 60)
    print("🎬 Testing InsureX Demo Flow")
    print("=" * 60)

    # Test /demo/run endpoint
    print("\n[TEST 1] Running complete demo flow...")
    print("Endpoint: POST /api/demo/run")

    response = requests.post(
        f"{BASE_URL}/demo/run",
        json={
            "worker_name": "Test Ravi",
            "zone": "Zone-D",
            "event_type": "HEAT"
        }
    )

    if response.status_code == 200:
        result = response.json()

        print("\n✅ Demo Successful!")
        print("-" * 60)
        print(f"📝 Summary: {result['demo_summary']}")
        print("-" * 60)

        print(f"\n👤 Worker: {result['worker']['name']}")
        print(f"📍 Zone: {result['worker']['zone']}")

        print(f"\n📋 Policy:")
        print(f"   Premium: ₹{result['policy']['premium']}")
        print(f"   Risk Score: {result['policy']['risk_score']}")

        print(f"\n💰 Wallet:")
        print(f"   Initial: ₹{result['wallet']['initial_balance']}")
        print(f"   After Premium: ₹{result['wallet']['after_premium']}")
        print(f"   Final: ₹{result['wallet']['final_balance']}")
        print(f"   Net Gain: ₹{result['wallet']['net_gain']}")

        print(f"\n⚡ Event:")
        print(f"   Type: {result['event']['type']}")
        print(f"   Value: {result['event']['value']}")

        print(f"\n🤖 Claim Automation:")
        print(f"   Eligible Workers: {result['claim_automation']['eligible_workers']}")
        print(f"   Approved: {result['claim_automation']['approved']}")
        print(f"   Flagged: {result['claim_automation']['flagged']}")
        print(f"   Total Payout: ₹{result['claim_automation']['total_payout']}")
        print(f"   Processing Time: {result['claim_automation']['processing_time_ms']}ms")

        print(f"\n📊 User Claim:")
        print(f"   Status: {result['user_claim']['status']}")
        print(f"   Payout: ₹{result['user_claim']['payout_amount']}")
        print(f"   Fraud Score: {result['user_claim']['fraud_score']}")
        print(f"   Risk Level: {result['user_claim']['risk_level']}")

        print("\n" + "=" * 60)
        print("🎉 All Tests Passed!")
        print("=" * 60)

        return True
    else:
        print(f"\n❌ Demo Failed: {response.status_code}")
        print(response.text)
        return False


def test_trigger_event():
    """Test event triggering"""
    print("\n[TEST 2] Triggering standalone event...")
    print("Endpoint: POST /api/demo/trigger-event")

    response = requests.post(
        f"{BASE_URL}/demo/trigger-event",
        json={
            "event_type": "RAIN",
            "zone": "Zone-B"
        }
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Event triggered: {result['summary']}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


def test_stats():
    """Test statistics endpoint"""
    print("\n[TEST 3] Getting statistics...")
    print("Endpoint: GET /api/demo/stats")

    response = requests.get(f"{BASE_URL}/demo/stats")

    if response.status_code == 200:
        result = response.json()
        print(f"✅ Statistics:")
        print(f"   Total Events: {result['total_events']}")
        print(f"   Total Claims: {result['total_claims']}")
        print(f"   Approved: {result['approved_claims']}")
        print(f"   Approval Rate: {result['approval_rate']}%")
        print(f"   Total Payout: ₹{result['total_payout']}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        return False


if __name__ == "__main__":
    try:
        # Run tests
        success = test_demo_flow()

        if success:
            test_trigger_event()
            test_stats()

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED - DEMO READY!")
            print("=" * 60)
            print("\nTo run demo:")
            print("  curl -X POST http://localhost:5000/api/demo/run")

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("Make sure backend is running:")
        print("  cd backend && python run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
