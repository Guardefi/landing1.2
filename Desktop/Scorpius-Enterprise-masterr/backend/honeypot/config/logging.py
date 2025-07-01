import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging():
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)

    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"honeypot_detector_{timestamp}.log")

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_format)

    # File handler (rotating logs)
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10485760, backupCount=5  # 10MB
    )
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s"
    )
    file_handler.setFormatter(file_format)

    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Create specialized loggers
    loggers = {
        "api": logging.getLogger("api"),
        "detector": logging.getLogger("detector"),
        "blockchain": logging.getLogger("blockchain"),
        "database": logging.getLogger("database"),
    }

    # Set levels for specialized loggers
    loggers["api"].setLevel(logging.INFO)
    loggers["detector"].setLevel(logging.DEBUG)
    loggers["blockchain"].setLevel(logging.INFO)
    loggers["database"].setLevel(logging.INFO)

    logging.info("Logging configured successfully")
    return loggers
