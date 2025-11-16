from __future__ import annotations

import hmac
import hashlib
import json
import time
from typing import Dict, Any, Optional

import httpx

from ..core.config import settings


class WebhookService:
    @staticmethod
    def _signature(secret: str, body: bytes) -> str:
        mac = hmac.new(secret.encode("utf-8"), body, hashlib.sha256)
        return "sha256=" + mac.hexdigest()

    @staticmethod
    async def attempt_send(
        url: str,
        event_type: str,
        data: Dict[str, Any],
        idempotency_key: Optional[str] = None,
        secret_override: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Single attempt to send a webhook with HMAC signature and timestamp.
        Returns dict with success, status_code (if any), and error (if any).
        """
        payload = {
            "event_id": data.get("event_id") or f"evt_{int(time.time()*1000)}",
            "event_type": event_type,
            "timestamp": data.get("timestamp") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "data": data.get("data", data),
        }
        body = json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
        secret = secret_override or getattr(settings, "INTEGRATION_HMAC_SECRET", "dev_secret")
        signature = WebhookService._signature(secret, body)
        ts = str(int(time.time()))

        headers = {
            "Content-Type": "application/json",
            "X-Signature": signature,
            "X-Timestamp": ts,
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key

        timeout = timeout_seconds or getattr(settings, "WEBHOOK_TIMEOUT_SECONDS", 5)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, content=body, headers=headers)
                ok = 200 <= resp.status_code < 300
                return {"success": ok, "status_code": resp.status_code, "response_text": resp.text}
        except httpx.ReadTimeout:
            return {"success": False, "error": "timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}


