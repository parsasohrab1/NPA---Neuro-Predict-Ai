"""
EHR / HIS integration service.

Hardened against unreliable upstream EHR/HIS systems:

* explicit per-call timeouts (connect / read separately),
* idempotent retry with exponential backoff for transient failures
  (5xx / connect / read / pool errors),
* never retry on 4xx (client errors are caller bugs, not transient),
* a single :class:`EHRError` wraps everything so call-sites do not have to
  handle ``httpx.HTTPError`` directly,
* ``send_prediction_result`` carries an ``Idempotency-Key`` so retries on
  network blips do not duplicate writes.

This module is import-light: it only depends on ``httpx``.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime
from typing import Any, Optional

import httpx

logger = logging.getLogger(__name__)


class EHRError(RuntimeError):
    """Raised when EHR communication fails (transport or HTTP)."""

    def __init__(self, message: str, *, status_code: Optional[int] = None) -> None:
        super().__init__(message)
        self.status_code = status_code


def _is_retryable_status(status: int) -> bool:
    return status in {408, 425, 429, 500, 502, 503, 504}


class EHRService:
    """EHR/HIS REST client with retries, timeouts and audit-friendly logging."""

    def __init__(
        self,
        ehr_api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        *,
        connect_timeout: float = 5.0,
        read_timeout: float = 15.0,
        max_retries: int = 3,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.ehr_api_url = (ehr_api_url or "").rstrip("/") or None
        self.api_key = api_key
        self._timeout = httpx.Timeout(
            connect=connect_timeout,
            read=read_timeout,
            write=read_timeout,
            pool=connect_timeout,
        )
        self.max_retries = max(0, max_retries)
        self.backoff_seconds = backoff_seconds

    # --- HTTP plumbing -----------------------------------------------------

    def _headers(self, *, idempotency_key: Optional[str] = None) -> dict[str, str]:
        headers: dict[str, str] = {
            "Accept": "application/json",
            "User-Agent": "NeuroPredict-AI/EHR",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[dict[str, Any]] = None,
        json: Optional[dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
    ) -> dict[str, Any]:
        if not self.ehr_api_url:
            raise EHRError("EHR API URL not configured")

        url = f"{self.ehr_api_url}{path}"
        attempt = 0
        last_error: Optional[Exception] = None
        while attempt <= self.max_retries:
            try:
                async with httpx.AsyncClient(timeout=self._timeout) as client:
                    response = await client.request(
                        method,
                        url,
                        params=params,
                        json=json,
                        headers=self._headers(idempotency_key=idempotency_key),
                    )
                if response.status_code >= 500 and _is_retryable_status(response.status_code):
                    raise httpx.HTTPStatusError(
                        f"EHR upstream {response.status_code}",
                        request=response.request,
                        response=response,
                    )
                if response.status_code >= 400:
                    logger.warning(
                        "EHR %s %s -> %s", method, path, response.status_code
                    )
                    raise EHRError(
                        f"EHR returned HTTP {response.status_code}",
                        status_code=response.status_code,
                    )
                if response.status_code == 204 or not response.content:
                    return {}
                return response.json()
            except (httpx.TimeoutException, httpx.TransportError) as exc:
                last_error = exc
            except httpx.HTTPStatusError as exc:
                last_error = exc

            attempt += 1
            if attempt > self.max_retries:
                break
            sleep_for = self.backoff_seconds * (2 ** (attempt - 1))
            logger.info(
                "EHR %s %s transient failure (attempt %d/%d); retrying in %.2fs",
                method,
                path,
                attempt,
                self.max_retries,
                sleep_for,
            )
            await asyncio.sleep(sleep_for)

        assert last_error is not None  # for type-checker
        raise EHRError(f"EHR request failed after retries: {last_error}") from last_error

    # --- Public API --------------------------------------------------------

    async def get_patient_data(self, patient_id: str) -> dict[str, Any]:
        if not self.ehr_api_url:
            return {}
        try:
            return await self._request("GET", f"/patients/{patient_id}")
        except EHRError as exc:
            if exc.status_code == 404:
                return {}
            raise

    async def get_patient_lab_results(
        self,
        patient_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        if not self.ehr_api_url:
            return []
        params: dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = await self._request(
            "GET", f"/patients/{patient_id}/lab-results", params=params or None
        )
        return list(data.get("results", []))

    async def get_patient_medications(self, patient_id: str) -> list[dict[str, Any]]:
        if not self.ehr_api_url:
            return []
        data = await self._request("GET", f"/patients/{patient_id}/medications")
        return list(data.get("medications", []))

    async def get_patient_vital_signs(
        self,
        patient_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        if not self.ehr_api_url:
            return []
        params: dict[str, Any] = {}
        if start_date:
            params["start_date"] = start_date
        if end_date:
            params["end_date"] = end_date
        data = await self._request(
            "GET", f"/patients/{patient_id}/vital-signs", params=params or None
        )
        return list(data.get("vital_signs", []))

    async def send_prediction_result(
        self,
        patient_id: str,
        prediction_result: dict[str, Any],
        *,
        idempotency_key: Optional[str] = None,
    ) -> bool:
        if not self.ehr_api_url:
            logger.warning("EHR API URL not configured; skipping prediction send")
            return False
        payload = {
            "patient_id": patient_id,
            "prediction": prediction_result,
            "timestamp": datetime.utcnow().isoformat(),
            "source": "NeuroPredict-AI",
        }
        try:
            await self._request(
                "POST",
                f"/patients/{patient_id}/predictions",
                json=payload,
                idempotency_key=idempotency_key or str(uuid.uuid4()),
            )
            return True
        except EHRError as exc:
            logger.error("Sending prediction to EHR failed: %s", exc)
            return False

    async def sync_patient_data(self, patient_id: str) -> dict[str, Any]:
        sync: dict[str, Any] = {
            "patient_id": patient_id,
            "timestamp": datetime.utcnow().isoformat(),
            "patient_data": {},
            "lab_results": [],
            "medications": [],
            "vital_signs": [],
            "success": False,
        }
        try:
            sync["patient_data"] = await self.get_patient_data(patient_id)
            sync["lab_results"] = await self.get_patient_lab_results(patient_id)
            sync["medications"] = await self.get_patient_medications(patient_id)
            sync["vital_signs"] = await self.get_patient_vital_signs(patient_id)
            sync["success"] = True
        except EHRError as exc:
            logger.error("Sync failed for patient %s: %s", patient_id, exc)
            sync["error"] = str(exc)
        return sync
