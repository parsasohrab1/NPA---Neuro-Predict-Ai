"""
Tests for the EHR service resilience layer.

We swap ``httpx.AsyncClient`` for one bound to a ``MockTransport`` via
``monkeypatch``, which undoes the patch automatically between tests. The
contract under test is:

* configurable retry on transient 5xx,
* no retry on 4xx,
* timeout / transport errors retried then surfaced as :class:`EHRError`,
* idempotency key sent on writes.
"""
from __future__ import annotations

import httpx
import pytest

from app.services.integration import ehr_service as ehr_mod
from app.services.integration.ehr_service import EHRError, EHRService

pytestmark = pytest.mark.unit


def _install_mock_transport(
    monkeypatch: pytest.MonkeyPatch, transport: httpx.MockTransport
) -> None:
    """Patch ``httpx.AsyncClient`` (as seen by ehr_service) to use ``transport``."""
    real_client = ehr_mod.httpx.AsyncClient

    class _Patched(real_client):  # type: ignore[misc]
        def __init__(self, *args, **inner_kwargs):
            inner_kwargs["transport"] = transport
            super().__init__(*args, **inner_kwargs)

    monkeypatch.setattr(ehr_mod.httpx, "AsyncClient", _Patched)


def _service(**kwargs) -> EHRService:
    defaults = {
        "ehr_api_url": "https://ehr.example/api",
        "api_key": "token",
        "connect_timeout": 1.0,
        "read_timeout": 1.0,
        "backoff_seconds": 0.0,
    }
    defaults.update(kwargs)
    return EHRService(**defaults)


@pytest.mark.asyncio
async def test_get_patient_returns_payload_on_200(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["Authorization"] == "Bearer token"
        return httpx.Response(200, json={"id": "MRN-1"})

    _install_mock_transport(monkeypatch, httpx.MockTransport(handler))
    data = await _service().get_patient_data("MRN-1")
    assert data == {"id": "MRN-1"}


@pytest.mark.asyncio
async def test_get_patient_returns_empty_dict_on_404(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _install_mock_transport(
        monkeypatch, httpx.MockTransport(lambda _r: httpx.Response(404))
    )
    data = await _service().get_patient_data("missing")
    assert data == {}


@pytest.mark.asyncio
async def test_4xx_does_not_retry_and_raises(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[int] = []

    def handler(_request: httpx.Request) -> httpx.Response:
        calls.append(1)
        return httpx.Response(401, json={"detail": "unauthorized"})

    _install_mock_transport(monkeypatch, httpx.MockTransport(handler))
    with pytest.raises(EHRError) as excinfo:
        await _service(max_retries=3).get_patient_lab_results("MRN-1")
    assert excinfo.value.status_code == 401
    assert len(calls) == 1


@pytest.mark.asyncio
async def test_5xx_retries_then_succeeds(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[int] = []

    def handler(_request: httpx.Request) -> httpx.Response:
        calls.append(1)
        if len(calls) < 3:
            return httpx.Response(503, json={"detail": "busy"})
        return httpx.Response(200, json={"medications": [{"id": "m1"}]})

    _install_mock_transport(monkeypatch, httpx.MockTransport(handler))
    meds = await _service(max_retries=3).get_patient_medications("MRN-1")
    assert meds == [{"id": "m1"}]
    assert len(calls) == 3


@pytest.mark.asyncio
async def test_send_prediction_includes_idempotency_key(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["idempotency"] = request.headers.get("Idempotency-Key", "")
        return httpx.Response(202)

    _install_mock_transport(monkeypatch, httpx.MockTransport(handler))
    ok = await _service().send_prediction_result(
        "MRN-1",
        {"disease_type": "alzheimer", "risk_score": 0.5},
        idempotency_key="abc-123",
    )
    assert ok is True
    assert captured["idempotency"] == "abc-123"


@pytest.mark.asyncio
async def test_get_patient_returns_empty_when_url_missing() -> None:
    service = EHRService(ehr_api_url=None)
    assert await service.get_patient_data("MRN-1") == {}
    assert await service.get_patient_lab_results("MRN-1") == []
    assert await service.get_patient_medications("MRN-1") == []
    assert await service.get_patient_vital_signs("MRN-1") == []
    assert await service.send_prediction_result("MRN-1", {}) is False
