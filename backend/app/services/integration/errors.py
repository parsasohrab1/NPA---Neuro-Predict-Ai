"""
Shared integration error types for honest not-configured / not-implemented responses.
"""
from __future__ import annotations

from typing import Any, Dict, Literal

IntegrationStatus = Literal["not_configured", "not_implemented"]


class IntegrationError(Exception):
    """Base error for external-system integration gaps."""

    def __init__(
        self,
        detail: str,
        *,
        status: IntegrationStatus,
        http_status: int,
    ) -> None:
        super().__init__(detail)
        self.detail = detail
        self.status: IntegrationStatus = status
        self.http_status = http_status

    def to_dict(self) -> Dict[str, Any]:
        return {"status": self.status, "detail": self.detail}


class IntegrationNotConfiguredError(IntegrationError):
    """Remote endpoint / credentials are missing (HTTP 503)."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail, status="not_configured", http_status=503)


class IntegrationNotImplementedError(IntegrationError):
    """Operation scaffolding exists but is not implemented (HTTP 501)."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail, status="not_implemented", http_status=501)
