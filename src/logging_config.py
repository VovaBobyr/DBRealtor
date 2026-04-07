"""Structlog configuration for the sreality scraper.

Call configure_logging() once at process startup before any log calls.

Environment variables:
    LOG_FORMAT   "json"   → one JSON object per line (production)
                 "pretty" → human-readable ConsoleRenderer (development, default)
    LOG_LEVEL    "DEBUG" | "INFO" | "WARNING" | "ERROR"  (default: INFO)
"""
import logging
import os
import sys

import structlog


def configure_logging(level: str = "INFO") -> None:
    """Configure structlog globally.

    Also bridges stdlib logging (httpx, sqlalchemy, alembic, …) so every log
    line — regardless of origin — is formatted consistently.
    """
    log_level = getattr(logging, level.upper(), logging.INFO)
    log_format = os.getenv("LOG_FORMAT", "pretty")

    shared_processors: list = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.ExceptionRenderer(),
    ]

    renderer = (
        structlog.processors.JSONRenderer()
        if log_format == "json"
        else structlog.dev.ConsoleRenderer(colors=True)
    )

    # --- structlog native loggers ---
    structlog.configure(
        processors=shared_processors + [renderer],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # --- stdlib bridge (httpx, sqlalchemy, alembic, …) ---
    # Routes all stdlib logging through the same structlog processor chain so
    # output format is consistent across all libraries.
    stdlib_handler = logging.StreamHandler(sys.stderr)
    stdlib_handler.setFormatter(
        structlog.stdlib.ProcessorFormatter(
            foreign_pre_chain=shared_processors,
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                renderer,
            ],
        )
    )
    root = logging.getLogger()
    root.handlers = [stdlib_handler]
    root.setLevel(log_level)
