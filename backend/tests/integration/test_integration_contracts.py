"""
Contract tests: integration endpoints must not pretend success when unconfigured.

When PACS / HL7 MLLP / remote FHIR env vars are unset, remote operations return
HTTP 501/503 with an explicit ``not_configured`` / ``not_implemented`` payload —
never HTTP 200 with empty success lists.
"""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from httpx import AsyncClient, Response

from app.services.integration.errors import IntegrationNotConfiguredError
from app.services.integration.fhir_service import FHIRService
from app.services.integration.hl7v2_service import HL7v2Service
from app.services.integration.pacs_service import PACSService


def _detail_status(payload) -> str | None:
    """FastAPI may nest ``detail`` as dict or leave status at top level."""
    if isinstance(payload, dict):
        if "status" in payload:
            return payload["status"]
        detail = payload.get("detail")
        if isinstance(detail, dict):
            return detail.get("status")
        if isinstance(detail, str):
            return None
    return None


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pacs_studies_not_configured(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/v1/pacs/studies?patient_id=PATIENT123",
        headers=auth_headers,
    )
    assert response.status_code in (501, 503)
    assert _detail_status(response.json()) in ("not_configured", "not_implemented")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pacs_retrieve_not_configured(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/v1/pacs/studies/1.2.840.113619.2.55.3.123456",
        headers=auth_headers,
    )
    assert response.status_code in (501, 503)
    assert _detail_status(response.json()) in ("not_configured", "not_implemented")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pacs_worklist_not_configured(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/v1/pacs/worklist?patient_id=PATIENT123",
        headers=auth_headers,
    )
    assert response.status_code in (501, 503)
    assert _detail_status(response.json()) in ("not_configured", "not_implemented")


@pytest.mark.asyncio
@pytest.mark.integration
async def test_pacs_status_reports_not_configured(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/pacs/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "not_configured"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hl7v2_send_not_configured(client: AsyncClient, auth_headers: dict):
    message = (
        "MSH|^~\\&|NEUROPREDICT|HOSPITAL|LAB|LAB|20240115100000||ORU^R01^ORU_R01|"
        "MSG002|P|2.5\rPID|1||PATIENT123|||||||\r"
    )
    response = await client.post(
        "/api/v1/hl7v2/send",
        json={"message": message},
        headers=auth_headers,
    )
    assert response.status_code == 503
    assert _detail_status(response.json()) == "not_configured"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_hl7v2_status_reports_not_configured(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/hl7v2/status", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "not_configured"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fhir_remote_search_not_configured(client: AsyncClient, auth_headers: dict):
    response = await client.get(
        "/api/v1/fhir/remote/Patient",
        headers=auth_headers,
    )
    assert response.status_code == 503
    assert _detail_status(response.json()) == "not_configured"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fhir_imaging_study_not_implemented(client: AsyncClient, auth_headers: dict):
    response = await client.get("/api/v1/fhir/ImagingStudy", headers=auth_headers)
    assert response.status_code == 501
    assert _detail_status(response.json()) == "not_implemented"


@pytest.mark.asyncio
@pytest.mark.integration
async def test_fhir_remote_status_reports_not_configured(
    client: AsyncClient, auth_headers: dict
):
    response = await client.get("/api/v1/fhir/remote/status", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "not_configured"


# --- Service-level contracts -------------------------------------------------


def test_pacs_service_raises_when_unconfigured():
    svc = PACSService(pacs_server_url=None)
    with pytest.raises(IntegrationNotConfiguredError) as exc:
        svc.query_patient_studies(patient_id="X")
    assert exc.value.status == "not_configured"


def test_hl7_service_raises_when_mllp_unconfigured():
    svc = HL7v2Service(mllp_host=None)
    msg = svc.create_admit_message(
        patient_id="P1",
        patient_name="DOE^JOHN",
        birth_date="19800101",
        gender="M",
        admission_date="20240115100000",
        admitting_doctor="DOC",
    )
    with pytest.raises(IntegrationNotConfiguredError):
        svc.send_message(msg)


def test_fhir_service_raises_when_remote_unconfigured():
    svc = FHIRService(remote_endpoint=None)
    with pytest.raises(IntegrationNotConfiguredError):
        svc.search_resources("Patient", {"name": "Doe"})


def test_fhir_search_uses_httpx_when_configured():
    svc = FHIRService(remote_endpoint="https://fhir.example.com/r4")
    mock_response = MagicMock(spec=Response)
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": 0,
        "entry": [],
    }

    with patch("app.services.integration.fhir_service.httpx.Client") as client_cls:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.get.return_value = mock_response
        client_cls.return_value = client

        result = svc.search_resources("Patient", {"name": "Doe"})

    assert result["resourceType"] == "Bundle"
    client.get.assert_called_once()
    args, kwargs = client.get.call_args
    assert args[0] == "https://fhir.example.com/r4/Patient"
    assert kwargs["params"] == {"name": "Doe"}


def test_fhir_read_uses_httpx_when_configured():
    svc = FHIRService(remote_endpoint="https://fhir.example.com/r4")
    mock_response = MagicMock(spec=Response)
    mock_response.raise_for_status = MagicMock()
    mock_response.json.return_value = {"resourceType": "Patient", "id": "123"}

    with patch("app.services.integration.fhir_service.httpx.Client") as client_cls:
        client = MagicMock()
        client.__enter__.return_value = client
        client.__exit__.return_value = False
        client.get.return_value = mock_response
        client_cls.return_value = client

        result = svc.read_resource("Patient", "123")

    assert result["id"] == "123"
    client.get.assert_called_once()
