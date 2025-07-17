"""
Rate limiting middleware
"""
import time
from typing import Dict, Tuple, Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
import redis.asyncio as redis
from datetime import datetime, timedelta

from app.core.config import settings


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting API requests"""
    
    def __init__(self, app):
        super().__init__(app)
        self.redis_client: Optional[redis.Redis] = None
        self.enabled = settings.ENABLE_RATE_LIMITING
        
    async def dispatch(self, request: Request, call_next) -> Response:
        if not self.enabled:
            return await call_next(request)
        
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        # Initialize Redis client if not already done
        if not self.redis_client:
            try:
                self.redis_client = await redis.from_url(settings.REDIS_URL)
            except Exception:
                # If Redis is not available, skip rate limiting
                return await call_next(request)
        
        # Get client identifier (IP or API key)
        client_id = self._get_client_id(request)
        
        # Check rate limits
        allowed, retry_after = await self._check_rate_limit(client_id, request.url.path)
        
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Too many requests. Please retry after {retry_after} seconds",
                    "retry_after": retry_after
                },
                headers={
                    "X-RateLimit-Limit": str(settings.RATE_LIMIT_PER_MINUTE),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(time.time()) + retry_after),
                    "Retry-After": str(retry_after)
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = await self._get_remaining_requests(client_id)
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_PER_MINUTE)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        
        return response
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier from request"""
        # Check for API key in header
        api_key = request.headers.get("X-API-Key")
        if api_key:
            return f"api_key:{api_key}"
        
        # Check for authenticated user
        if hasattr(request.state, "user_id") and request.state.user_id:
            return f"user:{request.state.user_id}"
        
        # Fall back to IP address
        client_ip = request.client.host if request.client else "unknown"
        return f"ip:{client_ip}"
    
    async def _check_rate_limit(self, client_id: str, path: str) -> Tuple[bool, int]:
        """Check if client has exceeded rate limit"""
        try:
            # Create keys for different time windows
            minute_key = f"rate_limit:minute:{client_id}:{int(time.time() // 60)}"
            hour_key = f"rate_limit:hour:{client_id}:{int(time.time() // 3600)}"
            
            # Check minute limit
            minute_count = await self.redis_client.incr(minute_key)
            if minute_count == 1:
                await self.redis_client.expire(minute_key, 60)
            
            if minute_count > settings.RATE_LIMIT_PER_MINUTE:
                return False, 60 - int(time.time() % 60)
            
            # Check hour limit
            hour_count = await self.redis_client.incr(hour_key)
            if hour_count == 1:
                await self.redis_client.expire(hour_key, 3600)
            
            if hour_count > settings.RATE_LIMIT_PER_HOUR:
                return False, 3600 - int(time.time() % 3600)
            
            return True, 0
            
        except Exception:
            # If Redis fails, allow the request
            return True, 0
    
    async def _get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for the current minute"""
        try:
            minute_key = f"rate_limit:minute:{client_id}:{int(time.time() // 60)}"
            count = await self.redis_client.get(minute_key)
            if count:
                return max(0, settings.RATE_LIMIT_PER_MINUTE - int(count))
            return settings.RATE_LIMIT_PER_MINUTE
        except Exception:
            return settings.RATE_LIMIT_PER_MINUTE