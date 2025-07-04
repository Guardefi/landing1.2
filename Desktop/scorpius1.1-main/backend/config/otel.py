import logging
import os
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
    SimpleSpanProcessor,
)
from opentelemetry.trace import set_tracer_provider

logger = logging.getLogger(__name__)


def setup_opentelemetry(app, service_name: str, env: str = "dev"):
    """
    Set up OpenTelemetry tracing for FastAPI application
    """
    try:
        # Create resource with service and environment information
        resource = Resource(
            attributes={
                "service.name": service_name,
                "service.environment": env,
                "service.version": os.getenv("SERVICE_VERSION", "1.0.0"),
            }
        )

        # Create trace provider
        trace_provider = TracerProvider(resource=resource)

        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317"),
            insecure=os.getenv("OTEL_EXPORTER_OTLP_INSECURE", "true") == "true",
        )

        # Add console exporter for development
        console_exporter = ConsoleSpanExporter()

        # Add processors
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
        if env == "dev":
            trace_provider.add_span_processor(SimpleSpanProcessor(console_exporter))

        # Set global trace provider
        set_tracer_provider(trace_provider)

        # Instrument FastAPI
        FastAPIInstrumentor.instrument_app(app)

        logger.info(f"OpenTelemetry tracing initialized for {service_name}")

    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")

    return trace.get_tracer(__name__)


def setup_metrics(app, service_name: str):
    """
    Set up Prometheus metrics for FastAPI application
    """
    try:
        from prometheus_fastapi_instrumentator import Instrumentator

        instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=["/metrics"],
        ).instrument(app)

        instrumentator.expose(app)
        logger.info(f"Prometheus metrics initialized for {service_name}")

    except Exception as e:
        logger.error(f"Failed to initialize Prometheus metrics: {e}")
