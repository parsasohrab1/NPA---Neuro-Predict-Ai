#!/usr/bin/env python
"""
Simple script to create admin user
"""
import asyncio
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.session import AsyncSessionLocal, init_db
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_admin():
    """Create admin user"""
    # Initialize database
    await init_db()
    
    async with AsyncSessionLocal() as session:
        try:
            from sqlalchemy import select
            
            # Check if admin exists
            result = await session.execute(
                select(User).where(User.username == 'admin')
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print("✅ Admin user already exists!")
                print(f"Username: {existing.username}")
                print(f"Email: {existing.email}")
                return existing
            
            # Create admin
            admin = User(
                email="admin@neuropredict.ai",
                username="admin",
                full_name="System Administrator",
                hashed_password=get_password_hash("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
                is_verified=True,
                institution="NeuroPredict-AI"
            )
            
            session.add(admin)
            await session.commit()
            await session.refresh(admin)
            
            print("✅ Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("\n⚠️  Please change this password in production!")
            
            return admin
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(create_admin())
