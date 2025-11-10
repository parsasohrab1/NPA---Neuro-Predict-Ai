"""
Monitoring & Observability Service
Prometheus metrics, Health checks, Logging
"""
import time
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, text
import psutil
import redis.asyncio as redis

from ..core.config import settings
from ..db.session import get_db


class MonitoringService:
    """Service for monitoring and observability"""
    
    @staticmethod
    async def get_health_status(db: AsyncSession = None) -> Dict[str, Any]:
        """Get comprehensive health status"""
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.APP_VERSION,
            "services": {}
        }
        
        # Database health
        try:
            if db:
                result = await db.execute(text("SELECT 1"))
                result.fetchone()
                health["services"]["database"] = {
                    "status": "healthy",
                    "response_time_ms": 0
                }
            else:
                health["services"]["database"] = {
                    "status": "unknown",
                    "message": "Database session not available"
                }
        except Exception as e:
            health["services"]["database"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["status"] = "degraded"
        
        # Redis health
        try:
            redis_client = redis.from_url(
                f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                decode_responses=True
            )
            start_time = time.time()
            await redis_client.ping()
            response_time = (time.time() - start_time) * 1000
            await redis_client.close()
            
            health["services"]["redis"] = {
                "status": "healthy",
                "response_time_ms": round(response_time, 2)
            }
        except Exception as e:
            health["services"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["status"] = "degraded"
        
        # System resources
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            health["services"]["system"] = {
                "status": "healthy",
                "cpu_percent": cpu_percent,
                "memory": {
                    "total_gb": round(memory.total / (1024**3), 2),
                    "used_gb": round(memory.used / (1024**3), 2),
                    "percent": memory.percent
                },
                "disk": {
                    "total_gb": round(disk.total / (1024**3), 2),
                    "used_gb": round(disk.used / (1024**3), 2),
                    "percent": round((disk.used / disk.total) * 100, 2)
                }
            }
            
            # Check if resources are critical
            if cpu_percent > 90 or memory.percent > 90 or disk.percent > 90:
                health["status"] = "degraded"
                health["services"]["system"]["status"] = "warning"
        except Exception as e:
            health["services"]["system"] = {
                "status": "unknown",
                "error": str(e)
            }
        
        return health
    
    @staticmethod
    async def get_metrics(db: AsyncSession = None) -> Dict[str, Any]:
        """Get Prometheus-style metrics"""
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "metrics": {}
        }
        
        # Database metrics
        if db:
            try:
                # Count users
                result = await db.execute(select(func.count()).select_from(text("users")))
                user_count = result.scalar()
                metrics["metrics"]["users_total"] = user_count
                
                # Count active sessions
                result = await db.execute(select(func.count()).select_from(text("user_sessions")))
                active_sessions = result.scalar()
                metrics["metrics"]["sessions_active"] = active_sessions
                
            except Exception as e:
                metrics["metrics"]["database_error"] = str(e)
        
        # System metrics
        try:
            metrics["metrics"]["cpu_usage_percent"] = psutil.cpu_percent(interval=0.1)
            metrics["metrics"]["memory_usage_percent"] = psutil.virtual_memory().percent
            metrics["metrics"]["disk_usage_percent"] = psutil.disk_usage('/').percent
        except Exception as e:
            metrics["metrics"]["system_error"] = str(e)
        
        return metrics
    
    @staticmethod
    def format_prometheus_metrics(metrics: Dict[str, Any]) -> str:
        """Format metrics in Prometheus format"""
        lines = []
        timestamp = int(datetime.utcnow().timestamp() * 1000)
        
        for key, value in metrics.get("metrics", {}).items():
            if isinstance(value, (int, float)):
                lines.append(f"{key} {value} {timestamp}")
            elif isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    if isinstance(sub_value, (int, float)):
                        lines.append(f"{key}_{sub_key} {sub_value} {timestamp}")
        
        return "\n".join(lines)

