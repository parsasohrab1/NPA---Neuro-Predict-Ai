"""
Test script to check Load All Datasets endpoint
"""
import requests
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:8000"

def test_load_datasets():
    """Test the load all datasets endpoint"""
    
    # First login to get token
    print("Step 1: Attempting to login...")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"username": "admin", "password": "admin123"},
            timeout=10,
            verify=False
        )
        
        if login_response.status_code == 200:
            token = login_response.json().get('access_token')
            print(f"[OK] Login successful! Token: {token[:20]}...")
        else:
            print(f"[ERROR] Login failed: {login_response.status_code}")
            print(f"  Response: {login_response.text[:200]}")
            print("\n[INFO] Trying without authentication...")
            token = None
    except Exception as e:
        print(f"[ERROR] Login error: {e}")
        token = None
    
    # Test load datasets endpoint
    print("\nStep 2: Testing load-all-datasets endpoint...")
    
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        print("  Making request (this may take a while)...")
        response = requests.post(
            f"{BASE_URL}/api/v1/disease-tracking/load-all-datasets",
            headers=headers,
            timeout=120,  # 2 minutes
            verify=False
        )
        
        print(f"\n  Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("  [SUCCESS]!")
            print(f"    Message: {data.get('message')}")
            print(f"    Patients: {data.get('total_patients', 0)}")
            print(f"    Records: {data.get('total_records', 0)}")
            print(f"    Predictions: {data.get('total_predictions', 0)}")
            print(f"    Skipped: {data.get('skipped', 0)}")
            
            if data.get('error_count', 0) > 0:
                print(f"    [WARNING] Errors: {data.get('error_count')}")
                print("    First few errors:")
                for i, err in enumerate(data.get('errors', [])[:5], 1):
                    print(f"      {i}. {err}")
        
        elif response.status_code == 401:
            print("  [ERROR] Authentication required")
            print("    You need to login first or provide valid credentials")
        
        elif response.status_code == 403:
            print("  [ERROR] Permission denied")
            print("    You need admin role to load datasets")
        
        elif response.status_code == 500:
            print("  [ERROR] Server error")
            try:
                detail = response.json().get('detail', response.text[:200])
                print(f"    Detail: {detail}")
            except:
                print(f"    Response: {response.text[:500]}")
        
        else:
            print(f"  [ERROR] Unexpected status: {response.status_code}")
            print(f"    Response: {response.text[:500]}")
    
    except requests.exceptions.Timeout:
        print("  [ERROR] Request timed out (>120s)")
        print("    The dataset might be too large or there's a processing issue")
    
    except Exception as e:
        print(f"  [ERROR] Error: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Load All Datasets Test")
    print("=" * 60)
    
    test_load_datasets()
    
    print("\n" + "=" * 60)
    print("Test completed!")
    print("=" * 60)

