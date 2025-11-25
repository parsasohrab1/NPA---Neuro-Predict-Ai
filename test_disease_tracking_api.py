"""
Test script to check Disease Tracking API connectivity and authentication
"""
import requests
import sys
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8000"

def test_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/disease-tracking/health", timeout=5, verify=False)
        if response.status_code == 200:
            print("[OK] Backend is running")
            print(f"  Response: {response.json()}")
            return True
        else:
            print(f"[ERROR] Backend returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to backend. Is it running on port 8000?")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_patients_summary_no_auth():
    """Test patients summary endpoint without authentication"""
    try:
        response = requests.get(f"{BASE_URL}/api/v1/disease-tracking/all-patients/summary", timeout=5, verify=False)
        print(f"\nTesting patients summary (no auth): Status {response.status_code}")
        if response.status_code == 401:
            print("  [EXPECTED] Authentication required")
            return True
        elif response.status_code == 200:
            print("  [OK] Success! Returned data:")
            data = response.json()
            print(f"    Total patients: {data.get('total_patients', 0)}")
            return True
        else:
            print(f"  [UNEXPECTED] Status: {response.status_code}")
            print(f"    Response: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False


def test_login():
    """Test login to get a token"""
    try:
        # Try to login with default credentials
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=5,
            verify=False
        )
        
        print(f"\nTesting login: Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            token = data.get('access_token')
            print(f"  [OK] Login successful! Token: {token[:20]}...")
            return token
        else:
            print(f"  [ERROR] Login failed: {response.text[:200]}")
            return None
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return None


def test_patients_summary_with_auth(token):
    """Test patients summary endpoint with authentication"""
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{BASE_URL}/api/v1/disease-tracking/all-patients/summary",
            headers=headers,
            timeout=5,
            verify=False
        )
        
        print(f"\nTesting patients summary (with auth): Status {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"  [OK] Success! Total patients: {data.get('total_patients', 0)}")
            print(f"    High risk Alzheimer: {data.get('high_risk_alzheimer', 0)}")
            print(f"    High risk Parkinson: {data.get('high_risk_parkinson', 0)}")
            return True
        elif response.status_code == 403:
            print(f"  [ERROR] Permission denied - need doctor role")
            return False
        else:
            print(f"  [ERROR] Failed: {response.text[:200]}")
            return False
    except Exception as e:
        print(f"  [ERROR] Error: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("Disease Tracking API Test")
    print("=" * 60)
    
    # Test 1: Health check
    health_ok = test_health()
    if not health_ok:
        print("\n[INFO] Health check had issues, but let's continue testing...")
        # Don't exit - the backend might still work for authenticated requests
    
    # Test 2: Without auth
    test_patients_summary_no_auth()
    
    # Test 3: With auth
    token = test_login()
    if token:
        test_patients_summary_with_auth(token)
    else:
        print("\n[WARNING] Could not test with authentication (login failed)")
        print("  You may need to create a user first or use different credentials")
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

