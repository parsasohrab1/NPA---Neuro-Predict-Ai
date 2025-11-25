"""
Create a test authentication token for development
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from jose import jwt
from datetime import datetime, timedelta
from app.core.config import settings

def create_test_token():
    """Create a test JWT token for development"""
    
    # Token payload
    payload = {
        "sub": "test_user@example.com",
        "user_id": 1,
        "role": "admin",  # admin has all permissions
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow(),
    }
    
    # Create token
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    
    print("\n" + "="*80)
    print("TEST AUTHENTICATION TOKEN")
    print("="*80)
    print(f"\nToken: {token}")
    print("\n" + "="*80)
    print("\nHow to use:")
    print("1. Open browser DevTools (F12)")
    print("2. Go to Console tab")
    print("3. Run: localStorage.setItem('auth_token', 'PASTE_TOKEN_HERE')")
    print("4. Refresh the page")
    print("\nOr copy this command:")
    print(f"localStorage.setItem('auth_token', '{token}')")
    print("="*80 + "\n")
    
    return token

if __name__ == "__main__":
    create_test_token()

