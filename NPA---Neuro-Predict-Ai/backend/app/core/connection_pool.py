"""
Connection Pooling Configuration
پیکربندی Connection Pooling
"""
from sqlalchemy.pool import QueuePool, NullPool
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from typing import Optional
import logging

from .config import settings

logger = logging.getLogger(__name__)


def create_optimized_engine():
    """
    Create optimized database engine with connection pooling
    
    Returns:
        Optimized async engine
    """
    # Connection pool settings
    pool_settings = {
        "pool_size": 20,  # Number of connections to maintain
        "max_overflow": 10,  # Additional connections beyond pool_size
        "pool_timeout": 30,  # Seconds to wait for connection
        "pool_recycle": 3600,  # Recycle connections after 1 hour
        "pool_pre_ping": True,  # Verify connections before using
        "echo": settings.DEBUG,  # Log SQL queries in debug mode
    }
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        **pool_settings
    )
    
    logger.info(
        f"Database engine created with pool_size={pool_settings['pool_size']}, "
        f"max_overflow={pool_settings['max_overflow']}"
    )
    
    return engine


def create_optimized_session_factory(engine) -> async_sessionmaker:
    """
    Create optimized session factory
    
    Args:
        engine: Database engine
    
    Returns:
        Session factory
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Don't expire objects on commit (better performance)
        autoflush=False,  # Don't autoflush (better control)
        autocommit=False
    )

