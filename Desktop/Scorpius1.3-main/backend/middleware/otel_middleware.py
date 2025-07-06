import logging
import time
from typing import Callable, Optional

from fastapi import Request, Response
from opentelemetry import trace
from opentelemetry.context import attach, detach
from opentelemetry.propagate import extract
from opentelemetry.trace.status import Status, StatusCode

logger = logging.getLogger(__name__)


class OpenTelemetryMiddleware:
    def __init__(self, app: Callable, tracer: Optional[trace.Tracer] = None):
        self.app = app
        self.tracer = tracer or trace.get_tracer(__name__)

    async def __call__(self, request: Request, call_next: Callable) -> Response:
        try:
            # Extract context from headers
            ctx = extract(request.headers)
            token = attach(ctx)

            # Start span
            with self.tracer.start_as_current_span(
                f"{request.method} {request.url.path}",
                kind=trace.SpanKind.SERVER,
                attributes={
                    "http.method": request.method,
                    "http.url": str(request.url),
                    "http.target": request.url.path,
                    "http.scheme": request.url.scheme,
                    "http.host": request.url.hostname,
                    "http.flavor": request.scope.get("http_version", "1.1"),
                    "net.peer.ip": request.client.host if request.client else None,
                },
            ) as span:
                start_time = time.time()

                # Call next middleware
                response = await call_next(request)

                # Set span attributes from response
                span.set_attributes(
                    {
                        "http.status_code": response.status_code,
                        "http.response_content_length": len(response.body)
                        if hasattr(response, "body")
                        else 0,
                    }
                )

                # Set span status
                if response.status_code >= 400:
                    span.set_status(Status(StatusCode.ERROR))

                # Add duration
                duration = time.time() - start_time
                span.set_attribute("http.duration", duration)

            detach(token)
            return response

        except Exception as e:
            logger.error(f"Error in OpenTelemetry middleware: {e}")
            raise
