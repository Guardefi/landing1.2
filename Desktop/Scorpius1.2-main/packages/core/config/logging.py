import logging
import os
from datetime import datetime
from typing import Dict, Any
import structlog
from structlog.processors import JSONRenderer
from structlog.stdlib import add_log_level, add_logger_name
from structlog.processors import TimeStamper
from structlog.processors import format_exc_info
from structlog.processors import StackInfoRenderer

# Define log levels
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

def configure_logging(
    level: str = 'INFO',
    json_format: bool = False,
    service_name: str = 'scorpius'
) -> None:
    """
    Configure structured logging
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Whether to use JSON format
        service_name: Name of the service
    """
    # Set up basic logging
    logging.basicConfig(
        level=LOG_LEVELS.get(level.upper(), logging.INFO),
        format='%(message)s'
    )

    # Create processors
    processors = [
        add_log_level,
        add_logger_name,
        TimeStamper(fmt="iso"),
        format_exc_info,
        StackInfoRenderer(),
        lambda _, __, event_dict: {
            **event_dict,
            "service": service_name,
            "timestamp": datetime.utcnow().isoformat(),
            "environment": os.getenv("ENVIRONMENT", "development")
        }
    ]

    # Add JSON renderer if needed
    if json_format:
        processors.append(JSONRenderer())
    else:
        processors.append(lambda _, __, event_dict: 
            f"[{event_dict['timestamp']}] {event_dict['level'].upper()} - {event_dict['event']}"
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

def get_logger(name: str) -> structlog.BoundLogger:
    """
    Get a configured logger
    
    Args:
        name: Name of the logger
        
    Returns:
        Configured logger
    """
    return structlog.get_logger(name)

def add_context(logger: structlog.BoundLogger, context: Dict[str, Any]) -> structlog.BoundLogger:
    """
    Add context to logger
    
    Args:
        logger: Logger instance
        context: Context dictionary
        
    Returns:
        Logger with added context
    """
    return logger.bind(**context)

def log_exception(
    logger: structlog.BoundLogger,
    error: Exception,
    context: Dict[str, Any] = None
) -> None:
    """
    Log an exception
    
    Args:
        logger: Logger instance
        error: Exception to log
        context: Additional context
    """
    if context is None:
        context = {}
    
    logger.error(
        "Exception occurred",
        error=str(error),
        traceback=str(error.__traceback__),
        **context
    )

def log_request(
    logger: structlog.BoundLogger,
    request: Any,
    response: Any,
    duration: float,
    context: Dict[str, Any] = None
) -> None:
    """
    Log a request
    
    Args:
        logger: Logger instance
        request: Request object
        response: Response object
        duration: Request duration in seconds
        context: Additional context
    """
    if context is None:
        context = {}
    
    logger.info(
        "Request completed",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration=f"{duration:.2f}s",
        **context
    )

def setup_sentry(
    dsn: str,
    environment: str = "production",
    service_name: str = "scorpius"
) -> None:
    """
    Configure Sentry for error reporting
    
    Args:
        dsn: Sentry DSN
        environment: Environment name
        service_name: Service name
    """
    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration
    
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        integrations=[
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR
            )
        ],
        traces_sample_rate=1.0,
        send_default_pii=True,
        release=f"{service_name}@{os.getenv('VERSION', 'unknown')}"
    )

def setup_loki(
    url: str,
    labels: Dict[str, str] = None
) -> None:
    """
    Configure Loki for log aggregation
    
    Args:
        url: Loki URL
        labels: Additional labels
    """
    if labels is None:
        labels = {}
    
    from structlog_loki import LokiHandler
    
    handler = LokiHandler(
        url=url,
        labels={
            "service": os.getenv("SERVICE_NAME", "scorpius"),
            "environment": os.getenv("ENVIRONMENT", "development"),
            **labels
        }
    )
    
    logging.getLogger().addHandler(handler)

def setup_prometheus(
    port: int = 8080,
    registry: str = "prometheus"
) -> None:
    """
    Configure Prometheus metrics
    
    Args:
        port: Port for Prometheus metrics
        registry: Prometheus registry
    """
    from prometheus_client import start_http_server
    
    start_http_server(port)
    
    # Add custom metrics
    from prometheus_client import Counter, Histogram
    
    REQUESTS = Counter(
        'http_requests_total',
        'Total HTTP requests',
        ['method', 'path', 'status_code']
    )
    
    REQUEST_LATENCY = Histogram(
        'http_request_duration_seconds',
        'HTTP request latency',
        ['method', 'path']
    )
