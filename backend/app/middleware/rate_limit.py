"""
Rate limiting middleware to prevent abuse
"""

import logging
import time
from typing import Callable, Dict
from collections import defaultdict
from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.config import settings

logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple in-memory rate limiting middleware
    For production, use Redis-based rate limiting
    """
    
    def __init__(self, app):
        super().__init__(app)
        # Store request counts: {ip: [(timestamp, count)]}
        self.request_counts: Dict[str, list] = defaultdict(list)
        self.minute_limit = settings.RATE_LIMIT_PER_MINUTE
        self.hour_limit = settings.RATE_LIMIT_PER_HOUR
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable
    ) -> Response:
        # Get client IP
        client_ip = self._get_client_ip(request)
        
        # Check rate limits
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Record this request
        self._record_request(client_ip)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self._get_remaining_requests(client_ip)
        response.headers["X-RateLimit-Limit"] = str(self.minute_limit)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract client IP from request"""
        # Check for forwarded IP (behind proxy/load balancer)
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0].strip()
        
        # Check for real IP header
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fall back to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits"""
        current_time = time.time()
        minute_ago = current_time - 60
        hour_ago = current_time - 3600
        
        # Get request history for this IP
        requests = self.request_counts.get(client_ip, [])
        
        # Count requests in last minute
        minute_count = sum(1 for ts in requests if ts > minute_ago)
        if minute_count >= self.minute_limit:
            return False
        
        # Count requests in last hour
        hour_count = sum(1 for ts in requests if ts > hour_ago)
        if hour_count >= self.hour_limit:
            return False
        
        return True
    
    def _record_request(self, client_ip: str) -> None:
        """Record a request for rate limiting"""
        current_time = time.time()
        hour_ago = current_time - 3600
        
        # Add current request
        self.request_counts[client_ip].append(current_time)
        
        # Clean up old entries (older than 1 hour)
        self.request_counts[client_ip] = [
            ts for ts in self.request_counts[client_ip] 
            if ts > hour_ago
        ]
    
    def _get_remaining_requests(self, client_ip: str) -> int:
        """Get remaining requests in current minute window"""
        current_time = time.time()
        minute_ago = current_time - 60
        
        requests = self.request_counts.get(client_ip, [])
        minute_count = sum(1 for ts in requests if ts > minute_ago)
        
        return max(0, self.minute_limit - minute_count)


class RedisRateLimiter:
    """
    Redis-based rate limiter for production use
    More scalable and works across multiple instances
    """
    
    def __init__(self, redis_client, prefix: str = "ratelimit"):
        self.redis = redis_client
        self.prefix = prefix
    
    async def is_allowed(
        self, 
        identifier: str, 
        limit: int, 
        window: int
    ) -> tuple[bool, int]:
        """
        Check if request is allowed within rate limit
        
        Args:
            identifier: Unique identifier (IP, user ID, etc.)
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, remaining_requests)
        """
        if not self.redis:
            return True, limit
        
        key = f"{self.prefix}:{identifier}"
        
        try:
            # Use Redis pipeline for atomic operations
            pipe = self.redis.pipeline()
            
            # Increment counter
            pipe.incr(key)
            # Set expiry if key is new
            pipe.expire(key, window)
            
            results = await pipe.execute()
            current_count = results[0]
            
            remaining = max(0, limit - current_count)
            is_allowed = current_count <= limit
            
            return is_allowed, remaining
            
        except Exception as e:
            logger.error(f"Redis rate limit error: {str(e)}")
            # Fail open - allow request if Redis is down
            return True, limit
