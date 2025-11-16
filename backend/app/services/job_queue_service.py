"""
Lightweight Job Queue using Redis (MVP)
"""
from __future__ import annotations

from typing import Optional, Dict, Any, Tuple
import json
import time
import uuid

import redis.asyncio as redis

from ..core.config import settings


class JobQueueService:
    DEFAULT_QUEUE = "queue:default"
    DLQ = "queue:dlq"

    _redis: Optional[redis.Redis] = None

    @staticmethod
    async def _get_redis() -> Optional[redis.Redis]:
        if JobQueueService._redis is None:
            try:
                JobQueueService._redis = redis.from_url(
                    f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
                    decode_responses=True,
                )
            except Exception:
                JobQueueService._redis = None
        return JobQueueService._redis

    @staticmethod
    async def enqueue(job_type: str, payload: Dict[str, Any], idempotency_key: Optional[str] = None, queue: Optional[str] = None) -> Dict[str, Any]:
        r = await JobQueueService._get_redis()
        if not r:
            raise RuntimeError("Redis not available")
        job_id = idempotency_key or f"job-{uuid.uuid4().hex}"
        # Idempotency: if a job with same key exists, return existing meta
        existing = await r.get(f"job:{job_id}:status")
        if existing:
            return {"enqueued": False, "job_id": job_id, "status": existing}
        job = {
            "job_id": job_id,
            "type": job_type,
            "payload": payload,
            "attempt": 0,
            "created_at": int(time.time()),
        }
        qname = queue or JobQueueService.DEFAULT_QUEUE
        await r.lpush(qname, json.dumps(job, ensure_ascii=False))
        await r.set(f"job:{job_id}:status", "queued", ex=24 * 3600)
        return {"enqueued": True, "job_id": job_id, "queue": qname}

    @staticmethod
    async def consume(queue: Optional[str] = None, timeout: int = 5) -> Optional[Dict[str, Any]]:
        r = await JobQueueService._get_redis()
        if not r:
            return None
        qname = queue or JobQueueService.DEFAULT_QUEUE
        res = await r.brpop(qname, timeout=timeout)
        if not res:
            return None
        _q, data = res
        try:
            job = json.loads(data)
            return job
        except Exception:
            return None

    @staticmethod
    async def ack(job_id: str, status: str = "completed") -> None:
        r = await JobQueueService._get_redis()
        if not r:
            return
        await r.set(f"job:{job_id}:status", status, ex=24 * 3600)

    @staticmethod
    async def retry(job: Dict[str, Any], backoff_seconds: int = 5, max_attempts: int = 5) -> None:
        r = await JobQueueService._get_redis()
        if not r:
            return
        job["attempt"] = int(job.get("attempt", 0)) + 1
        job_id = job.get("job_id")
        if job["attempt"] > max_attempts:
            await r.lpush(JobQueueService.DLQ, json.dumps(job, ensure_ascii=False))
            await r.set(f"job:{job_id}:status", "failed", ex=24 * 3600)
            return
        # simple backoff marker
        await r.set(f"job:{job_id}:status", f"retry_{job['attempt']}", ex=24 * 3600)
        # schedule by pushing back (MVP immediate push; a real delay needs a scheduler)
        await r.lpush(JobQueueService.DEFAULT_QUEUE, json.dumps(job, ensure_ascii=False))

    @staticmethod
    async def stats() -> Dict[str, Any]:
        r = await JobQueueService._get_redis()
        if not r:
            return {"available": False}
        length = await r.llen(JobQueueService.DEFAULT_QUEUE)
        dlq_len = await r.llen(JobQueueService.DLQ)
        return {"available": True, "queue_depth": length, "dlq_depth": dlq_len}

    @staticmethod
    async def list_dlq(limit: int = 50) -> list[Dict[str, Any]]:
        r = await JobQueueService._get_redis()
        if not r:
            return []
        # LRANGE returns newest at end; fetch recent items
        raw = await r.lrange(JobQueueService.DLQ, -limit, -1)
        out = []
        for item in raw:
            try:
                out.append(json.loads(item))
            except Exception:
                out.append({"raw": item})
        return out


