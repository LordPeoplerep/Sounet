"""
Rate Limiter Middleware
Simple in-memory rate limiting to prevent abuse.
"""

import time
import logging
from typing import Dict, Tuple
from collections import defaultdict
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger("souent.rate_limiter")


class RateLimiterMiddleware(BaseHTTPMiddleware):
    """
    Simple token bucket rate limiter.
    Tracks requests per IP address.
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Store: IP -> (tokens, last_refill_time)
        self._buckets: Dict[str, Tuple[float, float]] = defaultdict(
            lambda: (float(settings.RATE_LIMIT_REQUESTS), time.time())
        )
        self.max_tokens = settings.RATE_LIMIT_REQUESTS
        self.refill_rate = settings.RATE_LIMIT_REQUESTS / settings.RATE_LIMIT_PERIOD
    
    async def dispatch(self, request: Request, call_next):
        """Process request with rate limiting"""
        
        # Skip rate limiting for health checks
        if request.url.path in ["/", "/health", "/api/v1/system/health"]:
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limit
        allowed, remaining = self._check_rate_limit(client_ip)
        
        if not allowed:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "detail": f"Maximum {settings.RATE_LIMIT_REQUESTS} requests per {settings.RATE_LIMIT_PERIOD} seconds",
                    "retry_after": settings.RATE_LIMIT_PERIOD
                }
            )
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(int(remaining))
        response.headers["X-RateLimit-Reset"] = str(int(time.time() + settings.RATE_LIMIT_PERIOD))
        
        return response
    
    def _check_rate_limit(self, client_ip: str) -> Tuple[bool, float]:
        """
        Check if request is allowed under rate limit.
        
        Args:
            client_ip: Client IP address
            
        Returns:
            Tuple of (allowed: bool, remaining_tokens: float)
        """
        current_time = time.time()
        tokens, last_refill = self._buckets[client_ip]
        
        # Refill tokens based on time elapsed
        time_elapsed = current_time - last_refill
        tokens_to_add = time_elapsed * self.refill_rate
        tokens = min(self.max_tokens, tokens + tokens_to_add)
        
        # Check if request can be processed
        if tokens >= 1.0:
            tokens -= 1.0
            self._buckets[client_ip] = (tokens, current_time)
            return True, tokens
        else:
            self._buckets[client_ip] = (tokens, last_refill)
            return False, tokens
    
    def cleanup_old_entries(self):
        """Cleanup old IP entries to prevent memory bloat"""
        current_time = time.time()
        threshold = current_time - (settings.RATE_LIMIT_PERIOD * 10)
        
        old_ips = [
            ip for ip, (_, last_refill) in self._buckets.items()
            if last_refill < threshold
        ]
        
        for ip in old_ips:
            del self._buckets[ip]
        
        if old_ips:
            logger.debug(f"Cleaned up {len(old_ips)} old rate limit entries")
