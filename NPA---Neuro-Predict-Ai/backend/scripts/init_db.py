#!/usr/bin/env python
"""
Script to initialize database
"""
import asyncio
import sys
sys.path.insert(0, '/app')

from app.db.session import init_db


async def main():
    """Initialize database"""
    try:
        print("Initializing database...")
        await init_db()
        print("✅ Database initialized successfully!")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

