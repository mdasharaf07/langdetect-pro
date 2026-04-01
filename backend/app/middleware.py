"""
Custom middleware for API key authentication
"""

import time
from typing import Callable
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from auth import auth_manager
from schemas import ErrorResponse

class APIKeyAuthMiddleware(BaseHTTPMiddleware):
    """Middleware for API key authentication"""
    
    # Paths that don't require authentication
    PUBLIC_PATHS = {
        "/",           # Health check
        "/docs",       # Swagger docs
        "/redoc",      # ReDoc docs
        "/openapi.json", # OpenAPI schema
        "/register",   # User registration
        "/languages",  # Supported languages (public info)
        "/samples",    # Sample texts (public info)
        "/stats",      # Basic stats (public info)
    }
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Process request with API key authentication"""
        
        # Skip authentication for public paths
        if request.url.path in self.PUBLIC_PATHS:
            return await call_next(request)
        
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Get API key from headers
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponse(
                    error="API key required",
                    detail="Please provide an API key in the 'X-API-Key' header",
                    timestamp=datetime.now().isoformat()
                ).dict()
            )
        
        # Validate API key
        user = auth_manager.validate_api_key(api_key)
        if not user:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content=ErrorResponse(
                    error="Invalid API key",
                    detail="The provided API key is invalid or has been revoked",
                    timestamp=datetime.now().isoformat()
                ).dict()
            )
        
        # Check rate limiting
        if not self._check_rate_limit(user):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content=ErrorResponse(
                    error="Rate limit exceeded",
                    detail=f"Rate limit of {user.rate_limit} requests per hour exceeded",
                    timestamp=datetime.now().isoformat()
                ).dict()
            )
        
        # Add user info to request state for use in endpoints
        request.state.user = user
        request.state.api_key = api_key
        
        # Process request
        response = await call_next(request)
        
        # Add API usage headers
        response.headers["X-Rate-Limit-Limit"] = str(user.rate_limit)
        response.headers["X-Rate-Limit-Remaining"] = str(self._get_remaining_requests(user))
        response.headers["X-Rate-Limit-Reset"] = str(self._get_rate_limit_reset(user))
        
        return response
    
    def _check_rate_limit(self, user) -> bool:
        """Check if user has exceeded rate limit"""
        # Simple implementation: check requests in the last hour
        # In production, you'd want to use Redis or similar for proper rate limiting
        if user.request_count <= user.rate_limit:
            return True
        
        # If user has a last_used timestamp, check if it's been more than an hour
        if user.last_used:
            time_since_last_use = datetime.utcnow() - user.last_used
            if time_since_last_use > timedelta(hours=1):
                # Reset counter for new hour
                user.request_count = 1
                auth_manager.save_users()
                return True
        
        return False
    
    def _get_remaining_requests(self, user) -> int:
        """Get remaining requests for current hour"""
        remaining = user.rate_limit - user.request_count
        return max(0, remaining)
    
    def _get_rate_limit_reset(self, user) -> int:
        """Get Unix timestamp when rate limit resets"""
        if user.last_used:
            reset_time = user.last_used + timedelta(hours=1)
            return int(reset_time.timestamp())
        return int((datetime.utcnow() + timedelta(hours=1)).timestamp())

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for detailed request logging"""
    
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        """Log request details"""
        start_time = time.time()
        
        # Get user info if available
        user_id = None
        if hasattr(request.state, 'user'):
            user_id = request.state.user.id
        
        # Log request
        print(f"[{datetime.now().isoformat()}] {request.method} {request.url.path} - User: {user_id or 'Anonymous'}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        print(f"[{datetime.now().isoformat()}] {response.status_code} - {process_time:.3f}s")
        
        return response
