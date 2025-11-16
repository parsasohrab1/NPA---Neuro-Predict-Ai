"""
Structured JSON logging configuration and PII masking utilities.
"""
import logging
import re
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


EMAIL_PATTERN = re.compile(r"([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)")
PHONE_PATTERN = re.compile(r"(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{3}\)?[-.\s]?)?\d{3}[-.\s]?\d{4}")


def mask_pii(value: Optional[str]) -> Optional[str]:
    if not value or not isinstance(value, str):
        return value
    masked = EMAIL_PATTERN.sub(lambda m: f"{m.group(1)[:2]}***@***", value)
    masked = PHONE_PATTERN.sub("***-***-****", masked)
    return masked


class PIIMaskFilter(logging.Filter):
    """
    Masks PII in well-known fields before emission.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        # Mask common attributes if present
        for attr in ["user_email", "phone", "message"]:
            if hasattr(record, attr):
                try:
                    setattr(record, attr, mask_pii(getattr(record, attr)))
                except Exception:
                    # Best-effort mask; never break logging
                    pass
        return True


def setup_json_logging(service_name: str, environment: str, level: str = "INFO") -> None:
    """
    Configure root logger to emit structured JSON logs with stable fields.
    """
    root = logging.getLogger()
    # Avoid duplicate handlers if reconfigured (e.g., test reload)
    if root.handlers:
        for h in list(root.handlers):
            root.removeHandler(h)

    root.setLevel(getattr(logging, level.upper(), logging.INFO))

    log_handler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(levelname)s %(name)s %(message)s %(request_id)s %(user_id)s %(path)s %(method)s %(status_code)s %(latency_ms)s %(error_code)s %(service)s %(env)s"  # stable field set
    )
    log_handler.setFormatter(formatter)
    log_handler.addFilter(PIIMaskFilter())

    root.addHandler(log_handler)

    # Add default contextual data via a custom filter
    class ContextDefaults(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            setattr(record, "service", getattr(record, "service", service_name))
            setattr(record, "env", getattr(record, "env", environment))
            # Ensure all expected fields exist to keep schema stable
            for key, default in [
                ("request_id", None),
                ("user_id", None),
                ("path", None),
                ("method", None),
                ("status_code", None),
                ("latency_ms", None),
                ("error_code", None),
            ]:
                if not hasattr(record, key):
                    setattr(record, key, default)
            return True

    root.addFilter(ContextDefaults())


