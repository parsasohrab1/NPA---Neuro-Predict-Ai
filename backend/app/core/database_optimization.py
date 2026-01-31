"""
Database Optimization Utilities
ابزارهای بهینه‌سازی دیتابیس
"""
from sqlalchemy import Index, text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


# Database indexes for performance optimization
DATABASE_INDEXES = [
    # Patients table indexes
    Index('idx_patients_email', 'patients.email'),
    Index('idx_patients_date_of_birth', 'patients.date_of_birth'),
    Index('idx_patients_created_at', 'patients.created_at'),
    
    # Medical records indexes
    Index('idx_medical_records_patient_id', 'medical_records.patient_id'),
    Index('idx_medical_records_visit_date', 'medical_records.visit_date'),
    Index('idx_medical_records_patient_visit', 'medical_records.patient_id', 'medical_records.visit_date'),
    
    # Predictions indexes
    Index('idx_predictions_patient_id', 'predictions.patient_id'),
    Index('idx_predictions_created_at', 'predictions.created_at'),
    Index('idx_predictions_status', 'predictions.status'),
    Index('idx_predictions_patient_status', 'predictions.patient_id', 'predictions.status'),
    
    # Imaging studies indexes
    Index('idx_imaging_studies_patient_id', 'imaging_studies.patient_id'),
    Index('idx_imaging_studies_study_date', 'imaging_studies.study_date'),
    Index('idx_imaging_studies_modality', 'imaging_studies.modality'),
    
    # Audit logs indexes
    Index('idx_audit_logs_user_id', 'audit_logs.user_id'),
    Index('idx_audit_logs_timestamp', 'audit_logs.timestamp'),
    Index('idx_audit_logs_action', 'audit_logs.action'),
]


async def create_indexes(session: AsyncSession):
    """
    Create database indexes for performance optimization
    
    Args:
        session: Database session
    """
    try:
        for index in DATABASE_INDEXES:
            try:
                await session.execute(text(f"CREATE INDEX IF NOT EXISTS {index.name} ON {index.table.name} ({', '.join(index.columns)})"))
                logger.info(f"Created index: {index.name}")
            except Exception as e:
                logger.warning(f"Failed to create index {index.name}: {e}")
        
        await session.commit()
        logger.info("Database indexes created successfully")
    
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
        await session.rollback()


async def analyze_table(session: AsyncSession, table_name: str) -> Dict[str, Any]:
    """
    Analyze table statistics for query optimization
    
    Args:
        session: Database session
        table_name: Name of table to analyze
    
    Returns:
        Table statistics
    """
    try:
        result = await session.execute(
            text(f"ANALYZE {table_name}")
        )
        await session.commit()
        
        # Get table statistics
        stats_result = await session.execute(
            text(f"""
                SELECT 
                    schemaname,
                    tablename,
                    n_live_tup as row_count,
                    n_dead_tup as dead_rows,
                    last_vacuum,
                    last_autovacuum,
                    last_analyze,
                    last_autoanalyze
                FROM pg_stat_user_tables
                WHERE tablename = :table_name
            """),
            {"table_name": table_name}
        )
        
        stats = stats_result.fetchone()
        return {
            "table_name": table_name,
            "row_count": stats.n_live_tup if stats else 0,
            "dead_rows": stats.n_dead_tup if stats else 0,
            "last_analyze": stats.last_autoanalyze if stats else None
        }
    
    except Exception as e:
        logger.error(f"Error analyzing table {table_name}: {e}")
        return {}


async def vacuum_table(session: AsyncSession, table_name: str, full: bool = False):
    """
    Vacuum table to reclaim storage and update statistics
    
    Args:
        session: Database session
        table_name: Name of table to vacuum
        full: Whether to perform full vacuum
    """
    try:
        vacuum_type = "VACUUM FULL" if full else "VACUUM"
        await session.execute(text(f"{vacuum_type} {table_name}"))
        await session.commit()
        logger.info(f"Vacuumed table: {table_name}")
    
    except Exception as e:
        logger.error(f"Error vacuuming table {table_name}: {e}")
        await session.rollback()


async def get_slow_queries(session: AsyncSession, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get slow queries from PostgreSQL
    
    Args:
        session: Database session
        limit: Maximum number of queries to return
    
    Returns:
        List of slow queries
    """
    try:
        result = await session.execute(
            text("""
                SELECT 
                    query,
                    calls,
                    total_time,
                    mean_time,
                    max_time,
                    rows
                FROM pg_stat_statements
                WHERE mean_time > 100  -- Queries taking more than 100ms on average
                ORDER BY mean_time DESC
                LIMIT :limit
            """),
            {"limit": limit}
        )
        
        queries = []
        for row in result:
            queries.append({
                "query": row.query[:200],  # Truncate long queries
                "calls": row.calls,
                "total_time": row.total_time,
                "mean_time": row.mean_time,
                "max_time": row.max_time,
                "rows": row.rows
            })
        
        return queries
    
    except Exception as e:
        logger.error(f"Error getting slow queries: {e}")
        return []


async def optimize_query(session: AsyncSession, query: str) -> Dict[str, Any]:
    """
    Get query execution plan for optimization
    
    Args:
        session: Database session
        query: SQL query to analyze
    
    Returns:
        Query execution plan
    """
    try:
        result = await session.execute(
            text(f"EXPLAIN ANALYZE {query}")
        )
        
        plan = []
        for row in result:
            plan.append(row[0])
        
        return {
            "query": query,
            "plan": "\n".join(plan)
        }
    
    except Exception as e:
        logger.error(f"Error optimizing query: {e}")
        return {"query": query, "plan": str(e)}

