from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import redis
import time
import os
import logging
from typing import Callable, Optional
from ..auth.jwt import get_current_user
from functools import wraps

logger = logging.getLogger(__name__)

# Initialize Redis client
redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(redis_url)

# Default rate limits (requests per minute)
DEFAULT_RATE_LIMIT = 60  # 60 requests per minute
DEFAULT_BURST_LIMIT = 10  # 10 requests in burst

# Endpoint-specific rate limits
ENDPOINT_LIMITS = {
    "/api/v1/resumes/generate": 10,  # 10 requests per minute (resource intensive)
    "/api/v1/resumes/cover-letter": 10,
    "/api/v1/validate/resume": 20,
    "/api/v1/resumes/match-score": 30,
}

async def check_rate_limit(
    request: Request, 
    user_id: Optional[int] = None,
    rate_limit: int = DEFAULT_RATE_LIMIT,
    burst_limit: int = DEFAULT_BURST_LIMIT
) -> bool:
    """Check if request is within rate limits using a sliding window with Redis sorted sets"""
    # Determine the key based on user ID or IP address
    if user_id:
        key = f"rate_limit:{user_id}:{request.url.path}"
    else:
        # Use IP for unauthenticated requests
        client_ip = request.client.host
        key = f"rate_limit:ip:{client_ip}:{request.url.path}"
    
    # Current timestamp
    now = time.time()
    one_minute_ago = now - 60
    
    # Add current request to sorted set with score as timestamp
    redis_client.zadd(key, {str(now): now})
    
    # Remove requests older than 1 minute
    redis_client.zremrangebyscore(key, 0, one_minute_ago)
    
    # Set expiry on the key (cleanup)
    redis_client.expire(key, 120)  # 2 minutes TTL
    
    # Count requests in the last minute
    request_count = redis_client.zcard(key)
    
    # Count requests in the last 5 seconds (for burst protection)
    five_seconds_ago = now - 5
    burst_count = redis_client.zcount(key, five_seconds_ago, float('inf'))
    
    # Check if either limit is exceeded
    if request_count > rate_limit or burst_count > burst_limit:
        return False
    
    return True

def rate_limit(
    rate_limit: Optional[int] = None,
    burst_limit: Optional[int] = None,
    requests: Optional[int] = None,
    period: Optional[int] = None,
):
    """Decorator for rate limiting API endpoints.
    
    Accepts either:
      - rate_limit / burst_limit  (original signature)
      - requests / period         (alias: requests maps to rate_limit, period is ignored)
    """
    # Normalize: 'requests' is an alias for 'rate_limit'
    effective_rate_limit = rate_limit or requests
    
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Find the FastAPI Request object in function arguments
            request = None
            
            # First check kwargs for 'request' or common FastAPI parameter names
            for param_name in ['request', 'fastapi_request', 'req']:
                if param_name in kwargs and hasattr(kwargs[param_name], 'client'):
                    request = kwargs[param_name]
                    break
            
            # If not found in kwargs, check args
            if not request:
                for arg in args:
                    # Check if this is a FastAPI Request object
                    if hasattr(arg, 'client') and hasattr(arg, 'url') and hasattr(arg, 'method'):
                        request = arg
                        break
            
            if not request:
                # If still no request found, try to get it from the function signature inspection
                import inspect
                sig = inspect.signature(func)
                param_names = list(sig.parameters.keys())
                if args and len(args) > 0:
                    # Check if first argument could be request
                    first_arg = args[0]
                    if hasattr(first_arg, 'client') and hasattr(first_arg, 'url'):
                        request = first_arg
                
            if not request:
                # Log the issue but don't fail - allow the request through
                logger.warning(f"Rate limiter could not find Request object for {func.__name__}")
                return await func(*args, **kwargs)
            
            # Get endpoint-specific rate limit or use default
            endpoint_rate_limit = effective_rate_limit or ENDPOINT_LIMITS.get(request.url.path, DEFAULT_RATE_LIMIT)
            endpoint_burst_limit = burst_limit or DEFAULT_BURST_LIMIT
            
            # Get current user if authenticated
            user_id = None
            try:
                user = await get_current_user(request)
                user_id = user.id
            except:
                pass
            
            # Check rate limit
            is_allowed = await check_rate_limit(
                request, 
                user_id, 
                endpoint_rate_limit, 
                endpoint_burst_limit
            )
            
            if not is_allowed:
                return JSONResponse(
                    status_code=429,
                    content={
                        "detail": "Rate limit exceeded. Please try again later.",
                        "limit": endpoint_rate_limit,
                        "per": "minute"
                    }
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator