"""
Authentication middleware for protecting routes
"""

import logging
from typing import Callable
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.auth import decode_access_token

logger = logging.getLogger(__name__)

# Routes that don't require authentication
PUBLIC_ROUTES = [
    "/",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/auth/login",
    "/api/v1/auth/register",
    "/api/v1/auth/refresh",
    "/api/v1/auth/forgot-password",
]


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate JWT tokens on protected routes
    """
    
    async def dispatch(
        self, 
        request: Request, 
        call_next: Callable
    ) -> Response:
        # Skip authentication for public routes
        path = request.url.path
        
        if self._is_public_route(path):
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            # Allow request to proceed - actual auth check happens in route
            # This middleware just adds user info to request state if available
            return await call_next(request)
        
        # Extract token from "Bearer <token>"
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return await call_next(request)
            
            # Decode token and add user info to request state
            payload = decode_access_token(token)
            if payload:
                request.state.user_id = payload.get("sub")
                request.state.token_valid = True
            else:
                request.state.token_valid = False
                
        except ValueError:
            # Invalid header format
            request.state.token_valid = False
        except Exception as e:
            logger.error(f"Auth middleware error: {str(e)}")
            request.state.token_valid = False
        
        return await call_next(request)
    
    def _is_public_route(self, path: str) -> bool:
        """Check if route is public (no auth required)"""
        # Exact matches
        if path in PUBLIC_ROUTES:
            return True
        
        # Prefix matches (for nested public routes)
        public_prefixes = ["/docs", "/redoc", "/openapi"]
        for prefix in public_prefixes:
            if path.startswith(prefix):
                return True
        
        return False
