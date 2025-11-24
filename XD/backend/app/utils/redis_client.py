# -*- coding: utf-8 -*-
"""
Redis client utility for caching
"""

import redis
import json
import logging
from typing import Optional, Any
from functools import wraps

logger = logging.getLogger(__name__)

# Redis connection configuration - Using Redis Cloud
REDIS_URL = "redis://default:mqnXR9U01fIHWAjd9t5sHRCV24n1onmx@redis-15456.c8.us-east-1-4.ec2.cloud.redislabs.com:15456"

# Global Redis client instance
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get or create Redis client instance with connection pooling
    Returns None if Redis is unavailable
    """
    global _redis_client
    
    if _redis_client is None:
        try:
            # Use from_url for Redis Cloud connection
            _redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5,
                retry_on_timeout=True,
                health_check_interval=30,
                max_connections=50  # Connection pool size
            )
            # Test connection
            _redis_client.ping()
            logger.info(f"✅ Redis Cloud connection established successfully")
            logger.info(f"   URL: {REDIS_URL.split('@')[1]}")  # Log without password
        except (redis.ConnectionError, redis.TimeoutError) as e:
            logger.warning(f"⚠️ Redis connection failed: {e}. Caching will be disabled.")
            _redis_client = None
        except Exception as e:
            logger.error(f"❌ Unexpected Redis error: {e}")
            _redis_client = None
    
    return _redis_client


def cache_get(key: str) -> Optional[Any]:
    """
    Get value from Redis cache
    
    Args:
        key: Cache key
        
    Returns:
        Cached value (parsed from JSON) or None if not found or Redis unavailable
    """
    client = get_redis_client()
    if client is None:
        return None
    
    try:
        value = client.get(key)
        if value:
            return json.loads(value)
        return None
    except (redis.RedisError, json.JSONDecodeError) as e:
        logger.error(f"Error getting cache key '{key}': {e}")
        return None


def cache_set(key: str, value: Any, ttl: int = 300) -> bool:
    """
    Set value in Redis cache with TTL
    
    Args:
        key: Cache key
        value: Value to cache (will be JSON serialized)
        ttl: Time to live in seconds (default: 300 = 5 minutes)
        
    Returns:
        True if successful, False otherwise
    """
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        serialized = json.dumps(value, ensure_ascii=False, default=str)
        client.setex(key, ttl, serialized)
        logger.debug(f"Cached key '{key}' with TTL {ttl}s")
        return True
    except (redis.RedisError, TypeError, ValueError) as e:
        logger.error(f"Error setting cache key '{key}': {e}")
        return False


def cache_delete(key: str) -> bool:
    """
    Delete key from Redis cache
    
    Args:
        key: Cache key to delete
        
    Returns:
        True if successful, False otherwise
    """
    client = get_redis_client()
    if client is None:
        return False
    
    try:
        client.delete(key)
        logger.debug(f"Deleted cache key '{key}'")
        return True
    except redis.RedisError as e:
        logger.error(f"Error deleting cache key '{key}': {e}")
        return False


def cache_clear_pattern(pattern: str) -> int:
    """
    Clear all keys matching a pattern
    
    Args:
        pattern: Redis key pattern (e.g., "dashboard:*")
        
    Returns:
        Number of keys deleted
    """
    client = get_redis_client()
    if client is None:
        return 0
    
    try:
        keys = client.keys(pattern)
        if keys:
            deleted = client.delete(*keys)
            logger.info(f"Cleared {deleted} cache keys matching '{pattern}'")
            return deleted
        return 0
    except redis.RedisError as e:
        logger.error(f"Error clearing cache pattern '{pattern}': {e}")
        return 0


def with_cache(key_prefix: str, ttl: int = 300):
    """
    Decorator for caching function results
    
    Args:
        key_prefix: Prefix for cache key
        ttl: Time to live in seconds
        
    Usage:
        @with_cache("dashboard:overview", ttl=300)
        def get_dashboard_data(province: str):
            # ... expensive operation
            return data
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key from function arguments
            cache_key = f"{key_prefix}:{':'.join(str(arg) for arg in args)}"
            if kwargs:
                cache_key += f":{':'.join(f'{k}={v}' for k, v in sorted(kwargs.items()))}"
            
            # Try to get from cache
            cached_value = cache_get(cache_key)
            if cached_value is not None:
                logger.debug(f"Cache hit for key '{cache_key}'")
                return cached_value
            
            # Execute function and cache result
            logger.debug(f"Cache miss for key '{cache_key}'")
            result = func(*args, **kwargs)
            cache_set(cache_key, result, ttl)
            return result
        
        return wrapper
    return decorator


def get_cache_stats() -> dict:
    """
    Get Redis cache statistics
    
    Returns:
        Dictionary with cache stats or empty dict if Redis unavailable
    """
    client = get_redis_client()
    if client is None:
        return {"available": False}
    
    try:
        info = client.info("stats")
        return {
            "available": True,
            "total_connections": info.get("total_connections_received", 0),
            "total_commands": info.get("total_commands_processed", 0),
            "keyspace_hits": info.get("keyspace_hits", 0),
            "keyspace_misses": info.get("keyspace_misses", 0),
            "hit_rate": (
                info.get("keyspace_hits", 0) / 
                (info.get("keyspace_hits", 0) + info.get("keyspace_misses", 1))
            ) * 100
        }
    except redis.RedisError as e:
        logger.error(f"Error getting cache stats: {e}")
        return {"available": False, "error": str(e)}
