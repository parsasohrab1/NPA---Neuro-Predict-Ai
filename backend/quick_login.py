"""
Quick script to create admin user and get auth token
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from sqlalchemy import select
from app.db.session import async_session_maker
from app.models.user import User, UserRole
from app.core.security import get_password_hash, create_access_token


async def create_admin_and_login():
    """Create admin user if doesn't exist and return login token"""
    
    async with async_session_maker() as session:
        # Check if admin exists
        result = await session.execute(
            select(User).where(User.email == "admin@neuropredict.ai")
        )
        admin = result.scalar_one_or_none()
        
        if not admin:
            print("Creating admin user...")
            admin = User(
                email="admin@neuropredict.ai",
                username="admin",
                first_name="Admin",
                last_name="User",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_superuser=True,
            )
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            print("✓ Admin user created successfully!")
        else:
            print("✓ Admin user already exists")
        
        # Generate token
        token = create_access_token(
            data={"sub": admin.email, "role": admin.role.value}
        )
        
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS")
        print("="*60)
        print(f"Email:    admin@neuropredict.ai")
        print(f"Password: admin123")
        print(f"Role:     {admin.role.value}")
        print("="*60)
        print("\nAUTH TOKEN (for testing):")
        print("="*60)
        print(token)
        print("="*60)
        print("\nTo test in browser console:")
        print(f"localStorage.setItem('auth_token', '{token}')")
        print("\nThen refresh the page!")
        

if __name__ == "__main__":
    asyncio.run(create_admin_and_login())

