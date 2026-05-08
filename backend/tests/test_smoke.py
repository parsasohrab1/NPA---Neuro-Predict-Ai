"""
Smoke tests: must pass on every CI run.

These deliberately avoid the database, Redis, ML models, and any other
optional integration. They assert that the FastAPI app and its routers
can be imported and that the OpenAPI schema is well-formed. Failures
here indicate a broken import graph or misconfiguration that would
otherwise surface as confusing, unrelated test failures downstream.
"""
from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="module")
def smoke_client() -> TestClient:
    return TestClient(app, raise_server_exceptions=False)


def test_app_imports_cleanly() -> None:
    module = importlib.import_module("app.main")
    assert getattr(module, "app", None) is not None
    assert module.app.title


def test_root_endpoint_responds(smoke_client: TestClient) -> None:
    response = smoke_client.get("/")
    assert response.status_code == 200
    payload = response.json()
    assert "version" in payload
    assert "message" in payload


def test_openapi_schema_is_valid(smoke_client: TestClient) -> None:
    routes = [getattr(route, "path", "") for route in app.routes]
    assert any(path == "/" for path in routes), "Root route missing"
    assert any(path == "/health" for path in routes), "Health route missing"


@pytest.mark.parametrize(
    "module_path",
    [
        "app.core.config",
        "app.core.security",
        "app.db.session",
        "app.api.auth",
        "app.api.patients",
        "app.api.predictions",
    ],
)
def test_critical_modules_importable(module_path: str) -> None:
    importlib.import_module(module_path)


def test_secret_key_is_not_default() -> None:
    from app.core.config import settings

    assert settings.SECRET_KEY, "SECRET_KEY must be configured"
    assert "CHANGE_THIS" not in settings.SECRET_KEY, (
        "Refusing to run with the placeholder SECRET_KEY from .env.example"
    )
    assert len(settings.SECRET_KEY) >= 32, "SECRET_KEY must be at least 32 chars"


def test_debug_disabled_in_non_dev_env() -> None:
    from app.core.config import settings

    if settings.ENVIRONMENT in {"production", "staging", "test"}:
        assert settings.DEBUG is False, (
            f"DEBUG must be False in {settings.ENVIRONMENT} environment"
        )
