"""
Performance Optimization API Endpoints
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.security import get_current_user, require_role
from ..core.database_optimization import (
    create_indexes,
    analyze_table,
    get_slow_queries,
    optimize_query
)
from ..db.session import get_db
from ..models.user import User

router = APIRouter(prefix="/optimization", tags=["Performance Optimization"])


@router.post("/database/indexes")
async def create_database_indexes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Create database indexes for performance optimization
    
    Requires: Admin role
    """
    try:
        await create_indexes(db)
        return {
            "status": "success",
            "message": "Database indexes created successfully"
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating indexes: {str(e)}"
        )


@router.get("/database/analyze/{table_name}")
async def analyze_database_table(
    table_name: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Analyze table statistics for optimization
    
    Parameters:
        table_name: Name of table to analyze
    
    Requires: Admin role
    """
    try:
        stats = await analyze_table(db, table_name)
        return {
            "status": "success",
            "table_stats": stats
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error analyzing table: {str(e)}"
        )


@router.get("/database/slow-queries")
async def get_slow_database_queries(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get slow queries from database
    
    Parameters:
        limit: Maximum number of queries to return
    
    Requires: Admin role
    """
    try:
        queries = await get_slow_queries(db, limit)
        return {
            "status": "success",
            "count": len(queries),
            "queries": queries
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting slow queries: {str(e)}"
        )


@router.post("/database/optimize-query")
async def optimize_database_query(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role("admin"))
):
    """
    Get query execution plan for optimization
    
    Parameters:
        query: SQL query to analyze
    
    Requires: Admin role
    """
    try:
        plan = await optimize_query(db, query)
        return {
            "status": "success",
            "plan": plan
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error optimizing query: {str(e)}"
        )


@router.get("/cache/stats")
async def get_cache_statistics(
    current_user: User = Depends(require_role("admin"))
):
    """
    Get cache statistics
    
    Requires: Admin role
    """
    from ..core.cache import cache_service
    
    try:
        if not cache_service.enabled:
            return {
                "status": "disabled",
                "message": "Cache is not enabled"
            }
        
        # Get Redis info
        if cache_service.redis_client:
            info = await cache_service.redis_client.info()
            return {
                "status": "success",
                "enabled": True,
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory_human", "N/A"),
                "keyspace": info.get("db0", {})
            }
        
        return {
            "status": "success",
            "enabled": False
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting cache stats: {str(e)}"
        )


@router.post("/cache/clear")
async def clear_cache(
    prefix: str = None,
    current_user: User = Depends(require_role("admin"))
):
    """
    Clear cache
    
    Parameters:
        prefix: Optional prefix to clear (e.g., 'patient', 'prediction')
    
    Requires: Admin role
    """
    from ..core.cache import cache_service
    
    try:
        if prefix:
            deleted = await cache_service.delete_pattern(prefix, "*")
            return {
                "status": "success",
                "message": f"Cleared {deleted} keys with prefix '{prefix}'"
            }
        else:
            if cache_service.redis_client:
                await cache_service.redis_client.flushdb()
                return {
                    "status": "success",
                    "message": "Cache cleared successfully"
                }
            return {
                "status": "error",
                "message": "Cache not available"
            }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        )

