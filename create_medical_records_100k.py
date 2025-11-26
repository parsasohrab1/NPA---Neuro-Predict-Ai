"""
Create medical records and predictions for all 100,500 patients
Calls the /disease-tracking/load-all-datasets endpoint
"""
import requests
import time
from datetime import datetime

API_URL = 'http://localhost:8001/api/v1/disease-tracking/load-all-datasets'

print("="*90)
print("  📝 CREATING MEDICAL RECORDS & PREDICTIONS FOR 100,500 PATIENTS")
print("="*90)
print()
print("⏰ Start time:", datetime.now().strftime('%H:%M:%S'))
print()
print("🚀 Calling endpoint /disease-tracking/load-all-datasets...")
print("   This may take 20-30 minutes for 100,000 patients...")
print()

start_time = time.time()

try:
    # Make the API call with a long timeout
    response = requests.post(API_URL, timeout=3600)  # 1 hour timeout
    
    if response.status_code == 200:
        result = response.json()
        duration = time.time() - start_time
        
        print()
        print("="*90)
        print("  ✅ SUCCESS!")
        print("="*90)
        print()
        print("📊 Results:")
        print("   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()
        print(f"   Message: {result.get('message', 'N/A')}")
        print(f"   Patients processed: {result.get('total_patients', 0):,}")
        print(f"   Records created: {result.get('total_records', 0):,}")
        print(f"   Predictions created: {result.get('total_predictions', 0):,}")
        print(f"   Skipped: {result.get('skipped', 0):,}")
        print(f"   Errors: {result.get('error_count', 0):,}")
        print()
        print(f"   ⏱️  Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print()
        
        if result.get('errors'):
            print("⚠️  First 10 errors:")
            for error in result.get('errors', [])[:10]:
                print(f"      - {error}")
            print()
        
        print("="*90)
        print("  🎉 ALL DONE! Database is ready for Disease Tracking Dashboard!")
        print("="*90)
        print()
        
    else:
        print()
        print(f"❌ Error: HTTP {response.status_code}")
        print(f"Response: {response.text}")
        print()
        
except requests.exceptions.Timeout:
    print()
    print("❌ Timeout error: Request took too long (>1 hour)")
    print("   The operation may still be running on the backend.")
    print()
    
except requests.exceptions.ConnectionError:
    print()
    print("❌ Connection error: Cannot connect to backend")
    print("   Make sure backend is running on port 8001")
    print("   Run: powershell -ExecutionPolicy Bypass -File start_backend.ps1")
    print()
    
except Exception as e:
    print()
    print(f"❌ Error: {e}")
    print()
    
print()
print("⏰ End time:", datetime.now().strftime('%H:%M:%S'))
print()

