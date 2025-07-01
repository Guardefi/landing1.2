"""
OpenTelemetry Configuration for Scorpius Enterprise Platform
Implements distributed tracing, metrics, and logging with enterprise-grade observability.
"""

import logging
import os
from typing import Optional

from opentelemetry import trace, metrics
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.psycopg2 import Psycopg2Instrumentor
from opentelemetry.instrumentation.asyncio import AsyncioInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.system_metrics import SystemMetricsInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.semantic_conventions.resource import ResourceAttributes
from prometheus_client import start_http_server, CONTENT_TYPE_LATEST, generate_latest
from prometheus_fastapi_instrumentator import Instrumentator, metrics as prom_metrics

logger = logging.getLogger(__name__)


class ObservabilityConfig:
    """Configuration for observability components"""
    
    def __init__(self):
        self.service_name = os.getenv("SERVICE_NAME", "scorpius-unknown")
        self.service_version = os.getenv("SERVICE_VERSION", "1.0.0")
        self.environment = os.getenv("ENVIRONMENT", "development")
        
        # OTLP Configuration
        self.otlp_endpoint = os.getenv("OTLP_ENDPOINT", "http://tempo:4317")
        self.otlp_headers = os.getenv("OTLP_HEADERS", "")
        
        # Prometheus Configuration
        self.prometheus_port = int(os.getenv("PROMETHEUS_PORT", "9090"))
        self.prometheus_endpoint = os.getenv("PROMETHEUS_ENDPOINT", "/metrics")
        
        # Tracing Configuration
        self.enable_tracing = os.getenv("ENABLE_TRACING", "true").lower() == "true"
        self.trace_sampling_rate = float(os.getenv("TRACE_SAMPLING_RATE", "1.0"))
        
        # Metrics Configuration
        self.enable_metrics = os.getenv("ENABLE_METRICS", "true").lower() == "true"
        self.metrics_export_interval = int(os.getenv("METRICS_EXPORT_INTERVAL", "30"))


class ScorpiusObservability:
    """
    Enterprise observability manager for Scorpius Platform
    Provides centralized configuration for tracing, metrics, and logging
    """
    
    def __init__(self, config: Optional[ObservabilityConfig] = None):
        self.config = config or ObservabilityConfig()
        self._tracer_provider = None
        self._meter_provider = None
        self._instrumentator = None
        
    def setup_resource(self) -> Resource:
        """Create OpenTelemetry resource with service information"""
        return Resource.create({
            SERVICE_NAME: self.config.service_name,
            SERVICE_VERSION: self.config.service_version,
            ResourceAttributes.SERVICE_NAMESPACE: "scorpius",
            ResourceAttributes.DEPLOYMENT_ENVIRONMENT: self.config.environment,
            ResourceAttributes.SERVICE_INSTANCE_ID: os.getenv("HOSTNAME", "unknown"),
            "platform": "scorpius-enterprise",
            "component": "microservice"
        })
    
    def setup_tracing(self) -> None:
        """Configure distributed tracing with OTLP export"""
        if not self.config.enable_tracing:
            logger.info("🔍 Tracing disabled via configuration")
            return
            
        logger.info(f"🔍 Setting up tracing for {self.config.service_name}")
        
        # Create resource
        resource = self.setup_resource()
        
        # Create tracer provider
        self._tracer_provider = TracerProvider(resource=resource)
        
        # Configure OTLP exporter
        otlp_exporter = OTLPSpanExporter(
            endpoint=self.config.otlp_endpoint,
            headers=self._parse_headers(self.config.otlp_headers),
            insecure=True  # Use TLS in production
        )
        
        # Add span processor
        span_processor = BatchSpanProcessor(
            otlp_exporter,
            max_queue_size=2048,
            max_export_batch_size=512,
            export_timeout_millis=30000,
            schedule_delay_millis=5000
        )
        self._tracer_provider.add_span_processor(span_processor)
        
        # Set global tracer provider
        trace.set_tracer_provider(self._tracer_provider)
        
        logger.info("✅ Distributed tracing configured")
    
    def setup_metrics(self) -> None:
        """Configure metrics collection and export"""
        if not self.config.enable_metrics:
            logger.info("📊 Metrics disabled via configuration")
            return
            
        logger.info(f"📊 Setting up metrics for {self.config.service_name}")
        
        # Create resource
        resource = self.setup_resource()
        
        # Configure Prometheus reader
        prometheus_reader = PrometheusMetricReader()
        
        # Configure OTLP metric exporter
        otlp_metric_exporter = OTLPMetricExporter(
            endpoint=self.config.otlp_endpoint,
            headers=self._parse_headers(self.config.otlp_headers),
            insecure=True
        )
        
        otlp_reader = PeriodicExportingMetricReader(
            otlp_metric_exporter,
            export_interval_millis=self.config.metrics_export_interval * 1000
        )
        
        # Create meter provider with both readers
        self._meter_provider = MeterProvider(
            resource=resource,
            metric_readers=[prometheus_reader, otlp_reader]
        )
        
        # Set global meter provider
        metrics.set_meter_provider(self._meter_provider)
        
        logger.info("✅ Metrics collection configured")
    
    def setup_auto_instrumentation(self) -> None:
        """Configure automatic instrumentation for common libraries"""
        logger.info("🔧 Setting up automatic instrumentation")
        
        # FastAPI instrumentation
        FastAPIInstrumentor.instrument()
        
        # HTTP client instrumentation
        HTTPXClientInstrumentor().instrument()
        
        # Database instrumentation
        Psycopg2Instrumentor().instrument()
        RedisInstrumentor().instrument()
        
        # System instrumentation
        AsyncioInstrumentor().instrument()
        LoggingInstrumentor().instrument()
        
        # System metrics
        SystemMetricsInstrumentor().instrument()
        
        logger.info("✅ Auto-instrumentation configured")
    
    def setup_prometheus_fastapi(self, app) -> None:
        """Configure Prometheus metrics for FastAPI"""
        if not self.config.enable_metrics:
            return
            
        logger.info("📊 Setting up FastAPI Prometheus instrumentation")
        
        # Create instrumentator with custom configuration
        self._instrumentator = Instrumentator(
            should_group_status_codes=True,
            should_ignore_untemplated=True,
            should_respect_env_var=True,
            should_instrument_requests_inprogress=True,
            excluded_handlers=[".*admin.*", ".*health.*"],
            env_var_name="ENABLE_METRICS",
            inprogress_name="scorpius_http_requests_inprogress",
            inprogress_labels=True
        )
        
        # Add custom metrics
        self._instrumentator.add(
            prom_metrics.request_size(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="scorpius",
                metric_subsystem="http"
            )
        ).add(
            prom_metrics.response_size(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="scorpius",
                metric_subsystem="http"
            )
        ).add(
            prom_metrics.latency(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="scorpius",
                metric_subsystem="http"
            )
        ).add(
            prom_metrics.requests(
                should_include_handler=True,
                should_include_method=True,
                should_include_status=True,
                metric_namespace="scorpius",
                metric_subsystem="http"
            )
        )
        
        # Instrument the app
        self._instrumentator.instrument(app)
        
        # Expose metrics endpoint
        self._instrumentator.expose(app, endpoint="/metrics")
        
        logger.info("✅ FastAPI Prometheus instrumentation configured")
    
    def setup_custom_metrics(self):
        """Setup custom business metrics"""
        meter = metrics.get_meter("scorpius.custom", version="1.0.0")
        
        # Business metrics
        self.scan_requests_total = meter.create_counter(
            "scorpius_scan_requests_total",
            description="Total number of scan requests",
            unit="requests"
        )
        
        self.scan_duration = meter.create_histogram(
            "scorpius_scan_duration_seconds",
            description="Duration of scan operations",
            unit="seconds"
        )
        
        self.active_connections = meter.create_up_down_counter(
            "scorpius_active_websocket_connections",
            description="Number of active WebSocket connections",
            unit="connections"
        )
        
        self.vulnerability_severity = meter.create_counter(
            "scorpius_vulnerabilities_found_total",
            description="Total vulnerabilities found by severity",
            unit="vulnerabilities"
        )
        
        logger.info("✅ Custom metrics configured")
    
    def initialize(self, app=None) -> None:
        """Initialize all observability components"""
        logger.info("🚀 Initializing Scorpius observability stack")
        
        try:
            # Setup tracing
            self.setup_tracing()
            
            # Setup metrics
            self.setup_metrics()
            
            # Setup auto-instrumentation
            self.setup_auto_instrumentation()
            
            # Setup custom metrics
            self.setup_custom_metrics()
            
            # Setup FastAPI instrumentation if app provided
            if app:
                self.setup_prometheus_fastapi(app)
            
            logger.info("✅ Observability stack initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize observability: {e}")
            raise
    
    def shutdown(self) -> None:
        """Gracefully shutdown observability components"""
        logger.info("🛑 Shutting down observability components")
        
        if self._tracer_provider:
            self._tracer_provider.shutdown()
        
        if self._meter_provider:
            self._meter_provider.shutdown()
    
    def _parse_headers(self, headers_str: str) -> dict:
        """Parse OTLP headers from environment variable"""
        if not headers_str:
            return {}
        
        headers = {}
        for header in headers_str.split(","):
            if "=" in header:
                key, value = header.strip().split("=", 1)
                headers[key] = value
        
        return headers


# Global observability instance
_observability: Optional[ScorpiusObservability] = None


def get_observability() -> ScorpiusObservability:
    """Get global observability instance"""
    global _observability
    if _observability is None:
        _observability = ScorpiusObservability()
    return _observability


def initialize_observability(app=None, config: Optional[ObservabilityConfig] = None) -> ScorpiusObservability:
    """Initialize observability for the application"""
    global _observability
    _observability = ScorpiusObservability(config)
    _observability.initialize(app)
    return _observability


# Convenience functions for instrumentation
def get_tracer(name: str = None):
    """Get a tracer instance"""
    return trace.get_tracer(name or "scorpius.default")


def get_meter(name: str = None):
    """Get a meter instance"""
    return metrics.get_meter(name or "scorpius.default")
