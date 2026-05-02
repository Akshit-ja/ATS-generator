"""
Redis metrics collection module for OpenTelemetry instrumentation.
This module provides wrapper functions for Redis operations to track cache hits and misses.
"""

import functools
import logging
from typing import Any, Callable, Optional, TypeVar, cast

from ..core.telemetry import track_redis_cache, get_tracer

# Create a tracer for Redis operations
tracer = get_tracer("redis_operations")
logger = logging.getLogger(__name__)

T = TypeVar('T')

def track_redis_get(func: Callable) -> Callable:
    """
    Decorator to track Redis GET operations and record cache hits/misses.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        with tracer.start_as_current_span("redis_get_operation"):
            # Call the original function
            result = func(*args, **kwargs)
            
            # Track cache hit or miss
            hit = result is not None
            track_redis_cache(hit)
            
            return result
    return wrapper

def track_redis_set(func: Callable) -> Callable:
    """
    Decorator to track Redis SET operations.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        with tracer.start_as_current_span("redis_set_operation"):
            # Call the original function
            return func(*args, **kwargs)
    return wrapper

def instrument_redis_methods(cls):
    """
    Class decorator to instrument Redis methods in a class.
    """
    if hasattr(cls, '_get_from_cache'):
        cls._get_from_cache = track_redis_get(cls._get_from_cache)
    
    if hasattr(cls, '_save_to_cache'):
        cls._save_to_cache = track_redis_set(cls._save_to_cache)
    
    return cls