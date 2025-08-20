"""
Cache management for auth_sdk.
Handles Redis connections and caching operations with fallbacks.
"""
import json
import logging
from typing import Optional, Any

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

from .config import AuthConfig

logger = logging.getLogger(__name__)


class CacheManager:
    """Manages caching operations with Redis fallback support."""
    
    def __init__(self):
        self._redis_client = None
        self._redis_available = False
        
        if AuthConfig.ENABLE_CACHING and REDIS_AVAILABLE:
            self._initialize_redis()
    
    def _initialize_redis(self) -> None:
        """Initialize Redis connection with proper error handling."""
        try:
            redis_config = AuthConfig.get_redis_config()
            self._redis_client = redis.Redis(**redis_config)
            # Test connection
            self._redis_client.ping()
            self._redis_available = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
            self._redis_available = False
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if not self._redis_available:
            return None
            
        try:
            full_key = f"{AuthConfig.CACHE_PREFIX}:{key}"
            value = self._redis_client.get(full_key)
            return value.decode('utf-8') if value else None
        except Exception as e:
            logger.warning(f"Cache get failed for key {key}: {e}")
            return None
    
    def set(self, key: str, value: str, expiration: Optional[int] = None) -> bool:
        """Set value in cache with expiration."""
        if not self._redis_available:
            return False
            
        try:
            full_key = f"{AuthConfig.CACHE_PREFIX}:{key}"
            expiration = expiration or AuthConfig.CACHE_EXPIRATION
            
            if expiration > 0:
                self._redis_client.setex(full_key, expiration, value)
            else:
                self._redis_client.set(full_key, value)
            return True
        except Exception as e:
            logger.warning(f"Cache set failed for key {key}: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self._redis_available:
            return False
            
        try:
            full_key = f"{AuthConfig.CACHE_PREFIX}:{key}"
            self._redis_client.delete(full_key)
            return True
        except Exception as e:
            logger.warning(f"Cache delete failed for key {key}: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if cache is available."""
        return self._redis_available