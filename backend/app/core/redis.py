"""
Redis configuration and connection management
"""

import logging
from typing import Optional
import redis.asyncio as redis

from app.core.config import settings

logger = logging.getLogger(__name__)

# Global Redis client
redis_client: Optional[redis.Redis] = None


async def init_redis() -> None:
    """
    Initialize Redis connection
    """
    global redis_client
    
    try:
        redis_client = redis.from_url(
            settings.REDIS_URL,
            password=settings.REDIS_PASSWORD,
            encoding="utf-8",
            decode_responses=True,
        )
        
        # Test connection
        await redis_client.ping()
        logger.info("Redis connection established successfully")
        
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        logger.warning("Application starting without Redis - caching disabled")
        redis_client = None


async def close_redis() -> None:
    """
    Close Redis connection
    """
    global redis_client
    
    if redis_client:
        try:
            await redis_client.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {str(e)}")
        finally:
            redis_client = None


async def get_redis() -> Optional[redis.Redis]:
    """
    Get Redis client instance
    """
    return redis_client


async def check_redis_health() -> bool:
    """
    Check if Redis connection is healthy
    """
    if not redis_client:
        return False
    
    try:
        await redis_client.ping()
        return True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        return False


class RedisCache:
    """
    Redis cache helper class
    """
    
    def __init__(self, prefix: str = "ww"):
        self.prefix = prefix
    
    def _make_key(self, key: str) -> str:
        """Create prefixed cache key"""
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not redis_client:
            return None
        
        try:
            return await redis_client.get(self._make_key(key))
        except Exception as e:
            logger.error(f"Redis get error: {str(e)}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: str, 
        expire: int = 3600
    ) -> bool:
        """Set value in cache with expiration (default 1 hour)"""
        if not redis_client:
            return False
        
        try:
            await redis_client.setex(
                self._make_key(key), 
                expire, 
                value
            )
            return True
        except Exception as e:
            logger.error(f"Redis set error: {str(e)}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not redis_client:
            return False
        
        try:
            await redis_client.delete(self._make_key(key))
            return True
        except Exception as e:
            logger.error(f"Redis delete error: {str(e)}")
            return False
    
    async def exists(self, key: str) -> bool:
        """Check if key exists in cache"""
        if not redis_client:
            return False
        
        try:
            return await redis_client.exists(self._make_key(key)) > 0
        except Exception as e:
            logger.error(f"Redis exists error: {str(e)}")
            return False


# Create default cache instance
cache = RedisCache()
