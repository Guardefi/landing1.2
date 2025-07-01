"""Structured JSON logging configuration for API Gateway."""

import logging
import sys

import structlog

DEFAULT_LEVEL = logging.INFO


def configure_logging(level: int | str | None = None, json_logs: bool = True) -> None:
    """Configure root logging and structlog processors.

    Args:
        level: Logging level or name. If None, uses DEFAULT_LEVEL.
        json_logs: Output logs as JSON (True) or key-value pairs (False).
    """
    log_level = level or DEFAULT_LEVEL
    if isinstance(log_level, str):
        log_level = logging.getLevelName(log_level.upper())

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if json_logs:
        renderer: structlog.typing.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.KeyValueRenderer()

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.processors.add_log_level,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(log_level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
        cache_logger_on_first_use=True,
    )

    # Also set root logging handler so non-structlog modules output JSON too
    handler: logging.Handler
    if json_logs:
        handler = structlog.stdlib.ProcessorFormatter.wrap_for_formatter(
            structlog.processors.JSONRenderer()
        )
    else:
        handler = logging.StreamHandler(sys.stdout)

    root = logging.getLogger()
    root.setLevel(log_level)
    root.handlers.clear()
    handler.setLevel(log_level)
    root.addHandler(handler)
