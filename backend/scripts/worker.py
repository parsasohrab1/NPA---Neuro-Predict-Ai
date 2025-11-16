"""
Simple worker that consumes jobs from Redis and simulates execution.
Run: python -m backend.scripts.worker  (adjust PYTHONPATH) or `python backend/scripts/worker.py`
"""
import asyncio
import json
import time

from app.services.job_queue_service import JobQueueService


async def handle_job(job: dict):
    job_id = job.get("job_id")
    job_type = job.get("type")
    payload = job.get("payload", {})
    try:
        # Simulate different job types
        if job_type == "report.generate":
            await asyncio.sleep(0.1)
        elif job_type == "archive.run":
            await asyncio.sleep(0.05)
        elif job_type == "webhook.send":
            from app.services.webhook_service import WebhookService
            url = payload.get("url")
            event_type = payload.get("event_type", "event")
            data = payload.get("data", {})
            idk = job.get("job_id")
            result = await WebhookService.attempt_send(url, event_type, data, idempotency_key=idk)
            if not result.get("success"):
                # requeue for retry
                await JobQueueService.retry(job, backoff_seconds=2, max_attempts=5)
                return
        else:
            await asyncio.sleep(0.02)
        await JobQueueService.ack(job_id, status="completed")
    except Exception:
        await JobQueueService.retry(job, backoff_seconds=2, max_attempts=5)


async def main():
    print("Worker started...")
    while True:
        job = await JobQueueService.consume(timeout=2)
        if not job:
            await asyncio.sleep(0.2)
            continue
        await handle_job(job)


if __name__ == "__main__":
    asyncio.run(main())


