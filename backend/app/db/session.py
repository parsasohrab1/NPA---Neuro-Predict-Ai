"""
Database Session Management
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from ..core.config import settings

# Pool options only for non-SQLite (SQLite uses NullPool and rejects these)
_engine_kw: dict = {
    "echo": settings.DEBUG,
    "future": True,
}
if "sqlite" not in settings.DATABASE_URL:
    _engine_kw.update(
        pool_pre_ping=True,
        pool_size=20,
        max_overflow=10,
        pool_timeout=30,
        pool_recycle=3600,
    )
else:
    _engine_kw["connect_args"] = {"check_same_thread": False}

engine = create_async_engine(settings.DATABASE_URL, **_engine_kw)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Base class for models
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database - create all tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db():
    """Close database connections"""
    await engine.dispose()

