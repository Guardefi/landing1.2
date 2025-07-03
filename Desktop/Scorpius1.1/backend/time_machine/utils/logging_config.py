"""
Logging configuration for Time Machine
Provides structured logging with JSON output and multiple handlers
"""

import json
import logging
import logging.config
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging"""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON"""
        log_entry = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "thread": record.thread,
            "thread_name": record.threadName,
            "process": record.process,
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        for key, value in record.__dict__.items():
            if key not in [
                "name",
                "msg",
                "args",
                "levelname",
                "levelno",
                "pathname",
                "filename",
                "module",
                "lineno",
                "funcName",
                "created",
                "msecs",
                "relativeCreated",
                "thread",
                "threadName",
                "processName",
                "process",
                "getMessage",
                "exc_info",
                "exc_text",
                "stack_info",
            ]:
                log_entry[key] = value

        return json.dumps(log_entry, default=str)


class TimeMachineFilter(logging.Filter):
    """Custom filter for Time Machine logging"""

    def filter(self, record: logging.LogRecord) -> bool:
        """Filter log records"""
        # Add Time Machine context
        if not hasattr(record, "component"):
            record.component = "unknown"

        if not hasattr(record, "session_id"):
            record.session_id = None

        if not hasattr(record, "job_id"):
            record.job_id = None

        return True


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    enable_json: bool = True,
    enable_console: bool = True,
) -> None:
    """Setup logging configuration for Time Machine"""

    # Create logs directory if needed
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Base configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s [%(levelname)s] %(name)s:%(lineno)d in %(funcName)s(): %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "json": {
                "()": JSONFormatter,
            },
        },
        "filters": {
            "time_machine": {
                "()": TimeMachineFilter,
            }
        },
        "handlers": {},
        "loggers": {
            "time_machine": {"level": log_level, "handlers": [], "propagate": False},
            "uvicorn": {"level": "INFO", "handlers": [], "propagate": False},
            "fastapi": {"level": "INFO", "handlers": [], "propagate": False},
        },
        "root": {"level": "WARNING", "handlers": []},
    }

    # Console handler
    if enable_console:
        config["handlers"]["console"] = {
            "class": "logging.StreamHandler",
            "level": log_level,
            "formatter": "json" if enable_json else "detailed",
            "filters": ["time_machine"],
            "stream": "ext://sys.stdout",
        }
        config["loggers"]["time_machine"]["handlers"].append("console")
        config["loggers"]["uvicorn"]["handlers"].append("console")
        config["loggers"]["fastapi"]["handlers"].append("console")
        config["root"]["handlers"].append("console")

    # File handler
    if log_file:
        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": "json" if enable_json else "detailed",
            "filters": ["time_machine"],
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        }
        config["loggers"]["time_machine"]["handlers"].append("file")
        config["loggers"]["uvicorn"]["handlers"].append("file")
        config["loggers"]["fastapi"]["handlers"].append("file")
        config["root"]["handlers"].append("file")

    # Error file handler
    if log_file:
        error_file = str(Path(log_file).with_suffix(".error.log"))
        config["handlers"]["error_file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "ERROR",
            "formatter": "json" if enable_json else "detailed",
            "filters": ["time_machine"],
            "filename": error_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8",
        }
        config["loggers"]["time_machine"]["handlers"].append("error_file")
        config["loggers"]["uvicorn"]["handlers"].append("error_file")
        config["loggers"]["fastapi"]["handlers"].append("error_file")
        config["root"]["handlers"].append("error_file")

    # Apply configuration
    logging.config.dictConfig(config)


def get_logger(name: str, **context) -> logging.Logger:
    """Get logger with Time Machine context"""
    logger = logging.getLogger(f"time_machine.{name}")

    # Add context to all log records
    if context:
        old_factory = logging.getLogRecordFactory()

        def record_factory(*args, **kwargs):
            record = old_factory(*args, **kwargs)
            for key, value in context.items():
                setattr(record, key, value)
            return record

        logging.setLogRecordFactory(record_factory)

    return logger


def log_performance(logger: logging.Logger, operation: str, duration: float, **context):
    """Log performance metrics"""
    logger.info(
        f"Performance: {operation} completed in {duration:.3f}s",
        extra={
            "operation": operation,
            "duration_seconds": duration,
            "performance": True,
            **context,
        },
    )


def log_security_event(
    logger: logging.Logger, event_type: str, details: Dict[str, Any], **context
):
    """Log security events"""
    logger.warning(
        f"Security event: {event_type}",
        extra={
            "security_event": event_type,
            "security_details": details,
            "security": True,
            **context,
        },
    )


def log_audit_event(
    logger: logging.Logger, action: str, resource: str, user: str = None, **context
):
    """Log audit events"""
    logger.info(
        f"Audit: {action} on {resource}" + (f" by {user}" if user else ""),
        extra={
            "audit_action": action,
            "audit_resource": resource,
            "audit_user": user,
            "audit": True,
            **context,
        },
    )


class ContextLogger:
    """Logger wrapper that maintains context across operations"""

    def __init__(self, logger: logging.Logger, **context):
        self.logger = logger
        self.context = context

    def _log(self, level: int, msg: str, *args, **kwargs):
        """Log with context"""
        extra = kwargs.get("extra", {})
        extra.update(self.context)
        kwargs["extra"] = extra
        self.logger.log(level, msg, *args, **kwargs)

    def debug(self, msg: str, *args, **kwargs):
        self._log(logging.DEBUG, msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs):
        self._log(logging.INFO, msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs):
        self._log(logging.WARNING, msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs):
        self._log(logging.ERROR, msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs):
        self._log(logging.CRITICAL, msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs):
        kwargs["exc_info"] = True
        self.error(msg, *args, **kwargs)

    def with_context(self, **additional_context):
        """Create new logger with additional context"""
        new_context = {**self.context, **additional_context}
        return ContextLogger(self.logger, **new_context)


def get_context_logger(name: str, **context) -> ContextLogger:
    """Get context logger with Time Machine context"""
    logger = get_logger(name)
    return ContextLogger(logger, **context)


# Default configuration for production
PRODUCTION_CONFIG = {
    "log_level": "INFO",
    "log_file": "logs/time_machine.log",
    "enable_json": True,
    "enable_console": True,
}

# Default configuration for development
DEVELOPMENT_CONFIG = {
    "log_level": "DEBUG",
    "log_file": "logs/time_machine.dev.log",
    "enable_json": False,
    "enable_console": True,
}

# Default configuration for testing
TESTING_CONFIG = {
    "log_level": "WARNING",
    "log_file": None,
    "enable_json": False,
    "enable_console": False,
}


def configure_for_environment(env: str = "development"):
    """Configure logging for specific environment"""
    if env == "production":
        setup_logging(**PRODUCTION_CONFIG)
    elif env == "testing":
        setup_logging(**TESTING_CONFIG)
    else:  # development
        setup_logging(**DEVELOPMENT_CONFIG)


if __name__ == "__main__":
    # Demo logging setup
    setup_logging(log_level="DEBUG", enable_json=False)

    logger = get_context_logger("demo", component="test", session_id="demo-123")

    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")

    try:
        raise ValueError("Demo exception")
    except Exception:
        logger.exception("An exception occurred")

    log_performance(logger.logger, "test_operation", 1.234, items_processed=100)
    log_audit_event(logger.logger, "view", "snapshot_123", user="alice")
    log_security_event(
        logger.logger, "invalid_token", {"token": "***", "ip": "192.168.1.1"}
    )
