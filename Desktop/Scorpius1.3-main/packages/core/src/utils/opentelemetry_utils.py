import os
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_opentelemetry():
    """Configure OpenTelemetry with environment-based endpoint"""
    endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4318")
    
    # Initialize tracing
    trace.set_tracer_provider(TracerProvider())
    
    # Create OTLP exporter
    otlp_exporter = OTLPSpanExporter(
        endpoint=endpoint,
        insecure=True
    )
    
    # Create span processor
    span_processor = BatchSpanProcessor(otlp_exporter)
    
    # Add span processor to tracer provider
    trace.get_tracer_provider().add_span_processor(span_processor)

    return trace.get_tracer(__name__)
