#!/usr/bin/env python3
"""
Simple script to call /disease-tracking/load-all-datasets endpoint
"""
import requests
import time
from datetime import datetime

print("="*80)
print("  Creating Medical Records & Predictions for 100,500 Patients")
print("="*80)
print()
print("Start time:", datetime.now().strftime('%H:%M:%S'))
print("Estimated duration: 20-30 minutes")
print()
print("Calling /disease-tracking/load-all-datasets...")
print()

start_time = time.time()

try:
    response = requests.post(
        'http://localhost:8001/api/v1/disease-tracking/load-all-datasets',
        timeout=1800  # 30 minutes
    )
    
    duration = time.time() - start_time
    
    print()
    print("="*80)
    
    if response.status_code == 200:
        result = response.json()
        print("  SUCCESS!")
        print("="*80)
        print()
        print(f"Message: {result.get('message', 'N/A')}")
        print(f"Patients processed: {result.get('total_patients', 0):,}")
        print(f"Records created: {result.get('total_records', 0):,}")
        print(f"Predictions created: {result.get('total_predictions', 0):,}")
        print(f"Skipped: {result.get('skipped', 0):,}")
        print(f"Errors: {result.get('error_count', 0)}")
        print()
        print(f"Duration: {duration:.1f} seconds ({duration/60:.1f} minutes)")
        print()
        
        if result.get('errors'):
            print("First 10 errors:")
            for err in result.get('errors', [])[:10]:
                print(f"  - {err}")
            print()
    else:
        print(f"  ERROR: HTTP {response.status_code}")
        print("="*80)
        print()
        print(f"Response: {response.text}")
        print()
        
except requests.exceptions.Timeout:
    print("ERROR: Request timed out (>30 minutes)")
    print("The operation may still be running on the backend.")
    print()
    
except requests.exceptions.ConnectionError:
    print("ERROR: Cannot connect to backend")
    print("Make sure backend is running on port 8001")
    print()
    
except Exception as e:
    print(f"ERROR: {e}")
    print()

print("End time:", datetime.now().strftime('%H:%M:%S'))
print("="*80)

