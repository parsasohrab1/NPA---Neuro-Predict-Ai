#!/usr/bin/env python
"""
Script to create an admin user
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.db.session import AsyncSessionLocal
from app.models.user import User, UserRole
from app.core.security import get_password_hash


async def create_admin():
    """Create admin user"""
    async with AsyncSessionLocal() as session:
        try:
            # Check if admin exists
            from sqlalchemy import select
            result = await session.execute(
                select(User).where(User.username == 'admin')
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print("Admin user already exists!")
                return
            
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
            
            print("✅ Admin user created successfully!")
            print("Username: admin")
            print("Password: admin123")
            print("\n⚠️  Please change this password in production!")
            
        except Exception as e:
            print(f"❌ Error creating admin user: {e}")
            await session.rollback()


if __name__ == "__main__":
    asyncio.run(create_admin())

