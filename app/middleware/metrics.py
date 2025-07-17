"""
Prometheus metrics middleware
"""
import time
from typing import Callable
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from prometheus_client import Counter, Histogram, Gauge

from app.core.config import settings

# Define metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"]
)

ACTIVE_REQUESTS = Gauge(
    "http_requests_active",
    "Number of active HTTP requests"
)

ERROR_COUNT = Counter(
    "http_errors_total",
    "Total HTTP errors",
    ["method", "endpoint", "status"]
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware for collecting Prometheus metrics"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not settings.ENABLE_METRICS:
            return await call_next(request)
        
        # Skip metrics for metrics endpoint
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Start tracking
        ACTIVE_REQUESTS.inc()
        start_time = time.time()
        
        # Get endpoint path (remove path parameters)
        endpoint = self._normalize_endpoint(request.url.path)
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            # Count errors
            if response.status_code >= 400:
                ERROR_COUNT.labels(
                    method=request.method,
                    endpoint=endpoint,
                    status=response.status_code
                ).inc()
            
            return response
            
        except Exception as e:
            # Record error metrics
            duration = time.time() - start_time
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=500
            ).inc()
            
            ERROR_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=500
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=endpoint
            ).observe(duration)
            
            raise e
            
        finally:
            ACTIVE_REQUESTS.dec()
    
    def _normalize_endpoint(self, path: str) -> str:
        """Normalize endpoint path for metrics"""
        # Remove trailing slash
        path = path.rstrip("/")
        
        # Replace path parameters with placeholders
        parts = path.split("/")
        normalized_parts = []
        
        for i, part in enumerate(parts):
            # Common UUID pattern
            if len(part) == 36 and part.count("-") == 4:
                normalized_parts.append("{id}")
            # Numeric IDs
            elif part.isdigit():
                normalized_parts.append("{id}")
            # Keep static parts
            else:
                normalized_parts.append(part)
        
        return "/".join(normalized_parts) or "/"