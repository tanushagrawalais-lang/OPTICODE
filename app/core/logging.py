"""
OptiCode Backend A — Structured logging configuration.

Two formatters:
  - Development: human-readable, colorless single-line with request ID prefix
  - Production: JSON lines for log aggregation and search

Uses Python stdlib logging — no external dependency needed for Phase 1.
"""

import json
import logging
import sys
from datetime import UTC, datetime

from app.core.context import get_request_id


class _JSONFormatter(logging.Formatter):
    """Outputs each log record as a single-line JSON object."""

    def format(self, record: logging.LogRecord) -> str:
        data: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        rid = get_request_id()
        if rid:
            data["request_id"] = rid
        if record.exc_info and record.exc_info[0] is not None:
            data["exception"] = self.formatException(record.exc_info)
        return json.dumps(data, default=str)


class _DevFormatter(logging.Formatter):
    """Concise, human-readable lines for local development."""

    def format(self, record: logging.LogRecord) -> str:
        rid = get_request_id()
        rid_part = f" [{rid[:8]}]" if rid else ""
        line = f"{record.levelname:<8}{rid_part} {record.name}: {record.getMessage()}"
        if record.exc_info and record.exc_info[0] is not None:
            line += "\n" + self.formatException(record.exc_info)
        return line


def setup_logging(log_level: str = "INFO", environment: str = "development") -> None:
    """Configure the root logger for the application.

    Args:
        log_level: Python log level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).
        environment: 'production' selects JSON output; anything else selects dev output.
    """
    handler = logging.StreamHandler(sys.stdout)

    if environment == "production":
        handler.setFormatter(_JSONFormatter())
    else:
        handler.setFormatter(_DevFormatter())

    level = getattr(logging, log_level.upper(), logging.INFO)

    root = logging.getLogger()
    root.setLevel(level)
    root.handlers.clear()
    root.addHandler(handler)

    # Reduce noise from third-party libraries
    for noisy_logger in ("uvicorn.access", "httpx", "httpcore"):
        logging.getLogger(noisy_logger).setLevel(max(level, logging.WARNING))
