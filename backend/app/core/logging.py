from __future__ import annotations

import json
import logging
import sys
from logging.config import dictConfig
from typing import Any, MutableMapping

from .config import settings


class JsonFormatter(logging.Formatter):
    """JSON log formatter with trace_id support."""

    def format(self, record: logging.LogRecord) -> str:
        log_record: MutableMapping[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
        }
        if hasattr(record, "trace_id"):
            log_record["trace_id"] = getattr(record, "trace_id")
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record, ensure_ascii=False)


def configure_logging() -> None:
    """Configure logging for the application."""

    handlers: dict[str, Any] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": settings.log_level,
            "stream": sys.stdout,
            "formatter": "json" if settings.log_json else "standard",
        }
    }

    formatters: dict[str, Any] = {
        "standard": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        },
        "json": {
            "()": JsonFormatter,
        },
    }

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": formatters,
            "handlers": handlers,
            "root": {
                "level": settings.log_level,
                "handlers": ["console"],
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    configure_logging()
    return logging.getLogger(name)
