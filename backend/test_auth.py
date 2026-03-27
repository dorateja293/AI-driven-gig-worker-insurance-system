"""
Auth API Test - Test Login & Register

Tests the enhanced login and register endpoints.
"""

import requests
import json

BASE_URL = "http://localhost:5000/api"


def test_register():
    """Test user registration"""
    print("=" * 60)
    print("TEST 1: User Registration")
    print("=" * 60)

    data = {
        "name": "Test User",
        "phone": "9876543210",
        "city": "Mumbai",
        "zone": "Zone-B",
        "platform": "Zomato"
    }

    response = requests.post(f"{BASE_URL}/auth/register", json=data)

    if response.status_code == 201:
        result = response.json()
        print("✅ Registration Successful!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Name: {result['name']}")
        print(f"   Phone: {result['phone']}")
        print(f"   Zone: {result['zone']}")
        print(f"   Platform: {result['platform']}")
        print(f"   Wallet Balance: ₹{result['wallet_balance']}")
        print(f"   Token: {result['token'][:20]}...")
        return result
    elif response.status_code == 409:
        print("⚠️  User already exists, will use for login test")
        return {"phone": data['phone']}
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return None


def test_login(phone):
    """Test user login"""
    print("\n" + "=" * 60)
    print("TEST 2: User Login")
    print("=" * 60)

    data = {"phone": phone}

    response = requests.post(f"{BASE_URL}/auth/login", json=data)

    if response.status_code == 200:
        result = response.json()
        print("✅ Login Successful!")
        print(f"   User ID: {result['user_id']}")
        print(f"   Name: {result['name']}")
        print(f"   Phone: {result['phone']}")
        print(f"   City: {result['city']}")
        print(f"   Zone: {result['zone']}")
        print(f"   Platform: {result['platform']}")
        print(f"   Wallet Balance: ₹{result['wallet_balance']}")
        print(f"   Has Active Policy: {result['has_active_policy']}")

        if result['has_active_policy']:
            policy = result['active_policy']
            print(f"\n   📋 Active Policy:")
            print(f"      Policy ID: {policy['policy_id']}")
            print(f"      Premium: ₹{policy['premium']}")
            print(f"      Days Remaining: {policy['days_remaining']}")

        print(f"\n   Token: {result['token'][:20]}...")
        return result
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
        return None


def test_login_invalid():
    """Test login with invalid phone"""
    print("\n" + "=" * 60)
    print("TEST 3: Login with Invalid Phone")
    print("=" * 60)

    data = {"phone": "0000000000"}

    response = requests.post(f"{BASE_URL}/auth/login", json=data)

    if response.status_code == 404:
        print("✅ Correctly rejected invalid phone")
        print(f"   Error: {response.json()['error']}")
        return True
    else:
        print(f"❌ Unexpected response: {response.status_code}")
        return False


def test_get_current_user(token):
    """Test getting current user with token"""
    print("\n" + "=" * 60)
    print("TEST 4: Get Current User (Protected Route)")
    print("=" * 60)

    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(f"{BASE_URL}/auth/me", headers=headers)

    if response.status_code == 200:
        result = response.json()
        print("✅ Successfully retrieved user info with token")
        print(f"   User: {result['name']}")
        print(f"   Zone: {result['zone']}")
        return True
    else:
        print(f"❌ Failed: {response.status_code}")
        print(response.text)
        return False


def test_complete_flow():
    """Test complete auth flow with demo"""
    print("\n" + "=" * 60)
    print("TEST 5: Complete Flow with Demo")
    print("=" * 60)

    # Register
    print("\n[Step 1] Registering user...")
    reg_data = {
        "name": "Demo Ravi",
        "phone": "9123456789",
        "city": "Hyderabad",
        "zone": "Zone-D",
        "platform": "Swiggy"
    }

    reg_response = requests.post(f"{BASE_URL}/auth/register", json=reg_data)

    if reg_response.status_code in [201, 409]:
        print("✅ Step 1 complete")

        # Login
        print("\n[Step 2] Logging in...")
        login_response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"phone": reg_data['phone']}
        )

        if login_response.status_code == 200:
            login_result = login_response.json()
            print("✅ Step 2 complete")
            print(f"   Logged in as: {login_result['name']}")
            print(f"   Wallet: ₹{login_result['wallet_balance']}")

            return login_result
        else:
            print("❌ Login failed")
            return None
    else:
        print("❌ Registration failed")
        return None


if __name__ == "__main__":
    try:
        print("\n🔐 Testing InsureX Auth API\n")

        # Test 1: Register
        reg_result = test_register()

        if reg_result:
            phone = reg_result.get('phone')

            # Test 2: Login
            login_result = test_login(phone)

            if login_result:
                token = login_result['token']

                # Test 3: Invalid login
                test_login_invalid()

                # Test 4: Protected route
                test_get_current_user(token)

                # Test 5: Complete flow
                test_complete_flow()

                print("\n" + "=" * 60)
                print("✅ ALL AUTH TESTS PASSED!")
                print("=" * 60)
                print("\n📚 Auth Endpoints Available:")
                print("   POST /api/auth/register")
                print("   POST /api/auth/login")
                print("   GET  /api/auth/me (requires token)")
                print("\n💡 Login Usage:")
                print('   curl -X POST http://localhost:5000/api/auth/login \\')
                print('     -H "Content-Type: application/json" \\')
                print('     -d \'{"phone": "9876543210"}\'')

    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server")
        print("Make sure backend is running:")
        print("  cd backend && python run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
