# -*- coding: utf-8 -*-
"""
Cache Module for Farmme API
Supports Redis with fallback to in-memory cache
"""

import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# Try to import Redis
try:
    import redis
    from config import REDIS_URL
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logger.warning("⚠️  Redis not installed, using in-memory cache")

class RedisCache:
    """Redis cache implementation"""
    
    def __init__(self, redis_url: str):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                redis_url,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.connected = True
            logger.info(f"✅ Connected to Redis: {redis_url}")
        except Exception as e:
            self.connected = False
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis cache"""
        try:
            value = self.redis_client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in Redis cache with TTL"""
        try:
            serialized = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized)
            return True
        except Exception as e:
            logger.error(f"Redis set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from Redis cache"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache (use with caution)"""
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis clear error: {e}")
            return False
    
    def ping(self) -> bool:
        """Test Redis connection"""
        try:
            return self.redis_client.ping()
        except Exception as e:
            logger.error(f"Redis ping error: {e}")
            return False


class MockCache:
    """Mock cache implementation using in-memory dictionary"""
    
    def __init__(self):
        self._cache = {}
        self._expiry = {}
        logger.info("📦 Using in-memory cache (MockCache)")
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        try:
            if key in self._cache:
                # Check if expired
                if key in self._expiry and datetime.now() > self._expiry[key]:
                    del self._cache[key]
                    del self._expiry[key]
                    return None
                return self._cache[key]
            return None
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        try:
            self._cache[key] = value
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete value from cache"""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache"""
        try:
            self._cache.clear()
            self._expiry.clear()
            return True
        except Exception as e:
            logger.error(f"Cache clear error: {e}")
            return False

# Helper methods for both cache types
class CacheWrapper:
    """Wrapper to add helper methods"""
    
    def __init__(self, cache_instance):
        self._cache = cache_instance
    
    def get_prediction(self, data: dict) -> Optional[dict]:
        """Get cached prediction"""
        key = f"prediction:{json.dumps(data, sort_keys=True)}"
        return self._cache.get(key)
    
    def set_prediction(self, data: dict, result: dict, ttl: int = 3600) -> bool:
        """Cache prediction result"""
        key = f"prediction:{json.dumps(data, sort_keys=True)}"
        return self._cache.set(key, result, ttl)
    
    def get_recommendation(self, data: dict) -> Optional[dict]:
        """Get cached recommendation"""
        key = f"recommendation:{json.dumps(data, sort_keys=True)}"
        return self._cache.get(key)
    
    def set_recommendation(self, data: dict, result: dict, ttl: int = 1800) -> bool:
        """Cache recommendation result"""
        key = f"recommendation:{json.dumps(data, sort_keys=True)}"
        return self._cache.set(key, result, ttl)
    
    def get_session_data(self, user_id: int) -> Optional[dict]:
        """Get cached session data for user"""
        key = f"session:{user_id}"
        return self._cache.get(key)
    
    def set_session_data(self, user_id: int, data: dict, ttl_hours: int = 24) -> bool:
        """Cache session data for user"""
        key = f"session:{user_id}"
        ttl_seconds = ttl_hours * 3600
        return self._cache.set(key, data, ttl_seconds)
    
    def delete_session_data(self, user_id: int) -> bool:
        """Delete cached session data for user"""
        key = f"session:{user_id}"
        return self._cache.delete(key)
    
    def get_provinces_cache(self) -> Optional[list]:
        """Get cached provinces list"""
        key = "provinces:all"
        return self._cache.get(key)
    
    def set_provinces_cache(self, provinces: list, ttl: int = 3600) -> bool:
        """Cache provinces list (default 1 hour TTL)"""
        key = "provinces:all"
        return self._cache.set(key, provinces, ttl)
    
    def get_province_regions_cache(self) -> Optional[dict]:
        """Get cached province-region mapping"""
        key = "provinces:regions"
        return self._cache.get(key)
    
    def set_province_regions_cache(self, regions: dict, ttl: int = 3600) -> bool:
        """Cache province-region mapping (default 1 hour TTL)"""
        key = "provinces:regions"
        return self._cache.set(key, regions, ttl)
    
    def __getattr__(self, name):
        """Delegate all other methods to underlying cache"""
        return getattr(self._cache, name)


# Initialize global cache instance
def create_cache():
    """Create cache instance with Redis or fallback to MockCache"""
    if REDIS_AVAILABLE:
        try:
            from config import REDIS_URL, REDIS_ENABLED
            if REDIS_ENABLED:
                redis_cache = RedisCache(REDIS_URL)
                return CacheWrapper(redis_cache)
            else:
                logger.info("Redis disabled by configuration, using MockCache")
                return CacheWrapper(MockCache())
        except Exception as e:
            logger.warning(f"⚠️  Redis connection failed, falling back to MockCache: {e}")
            return CacheWrapper(MockCache())
    else:
        return CacheWrapper(MockCache())


cache = create_cache()
logger.info("✅ Cache module loaded successfully")