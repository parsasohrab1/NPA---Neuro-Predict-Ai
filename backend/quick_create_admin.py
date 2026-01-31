#!/usr/bin/env python
"""Quick script to create admin user via API"""
import requests
import json

try:
    # Try to create admin via API
    response = requests.post(
        "http://localhost:8001/api/v1/auth/create-test-admin",
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    if response.status_code == 200 or response.status_code == 201:
        data = response.json()
        print("[OK] Admin user created successfully!")
        print(f"Username: {data.get('username', 'admin')}")
        print(f"Email: {data.get('email', 'admin@neuropredict.ai')}")
    elif response.status_code == 400 and "already exists" in response.text.lower():
        print("[OK] Admin user already exists!")
        print("Username: admin")
        print("Password: admin123")
    else:
        print(f"[ERROR] Status: {response.status_code}")
        print(response.text)
except requests.exceptions.RequestException as e:
    print(f"[ERROR] Connection error: {e}")
    print("\nPlease make sure the backend is running on http://localhost:8001")
    print("Trying alternative method...")
    
    # Alternative: try to register a new user
    try:
        register_data = {
            "email": "admin@neuropredict.ai",
            "username": "admin",
            "password": "admin123",
            "full_name": "System Administrator",
            "role": "admin"
        }
        response = requests.post(
            "http://localhost:8001/api/v1/auth/register",
            json=register_data,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        if response.status_code in [200, 201]:
            print("[OK] Admin user registered successfully!")
        else:
            print(f"[ERROR] Registration failed: {response.status_code}")
            print(response.text)
    except Exception as e2:
        print(f"[ERROR] Registration also failed: {e2}")
