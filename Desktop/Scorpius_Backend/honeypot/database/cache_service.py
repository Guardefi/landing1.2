"""
Cache service for the honeypot detector using Redis
"""
import json
import logging
import aioredis
from typing import Any, Dict, List, Optional, Union, TypeVar, Generic
from datetime import datetime, timedelta

from config.settings import settings

# Configure logger
logger = logging.getLogger("database.cache_service")

# Generic type for cache values
T = TypeVar('T')


class CacheService:
    """Redis-based cache service for the honeypot detector"""
    
    def __init__(self):
        """Initialize cache service"""
        self.redis = None
        self.initialized = False
        
    async def initialize(self):
        """Connect to Redis"""
        try:
            logger.info(f"Connecting to Redis at {settings.REDIS_URL}")
            self.redis = await aioredis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            self.initialized = True
            logger.info("Connected to Redis successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}", exc_info=True)
            self.initialized = False
    
    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            self.initialized = False
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        if not self.initialized:
            return None
            
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
            
        except Exception as e:
            logger.error(f"Error getting value from cache: {e}", exc_info=True)
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache
        
        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
            ttl: Time to live in seconds, None for default TTL
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            ttl = ttl or settings.CACHE_TTL
            serialized = json.dumps(value)
            await self.redis.set(key, serialized, ex=ttl)
            return True
            
        except Exception as e:
            logger.error(f"Error setting value in cache: {e}", exc_info=True)
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            await self.redis.delete(key)
            return True
            
        except Exception as e:
            logger.error(f"Error deleting value from cache: {e}", exc_info=True)
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        
        Args:
            key: Cache key
            
        Returns:
            True if exists, False otherwise
        """
        if not self.initialized:
            return False
            
        try:
            return bool(await self.redis.exists(key))
            
        except Exception as e:
            logger.error(f"Error checking key existence in cache: {e}", exc_info=True)
            return False

    async def clear_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching pattern
        
        Args:
            pattern: Redis key pattern (e.g., "analysis:*")
            
        Returns:
            Number of keys deleted
        """
        if not self.initialized:
            return 0
            
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
            
        except Exception as e:
            logger.error(f"Error deleting keys by pattern from cache: {e}", exc_info=True)
            return 0
    
    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> Optional[int]:
        """
        Increment counter in cache
        
        Args:
            key: Cache key
            amount: Amount to increment
            ttl: Time to live in seconds
            
        Returns:
            New value or None on error
        """
        if not self.initialized:
            return None
            
        try:
            value = await self.redis.incrby(key, amount)
            
            # Set TTL if specified
            if ttl is not None:
                await self.redis.expire(key, ttl)
                
            return value
            
        except Exception as e:
            logger.error(f"Error incrementing counter in cache: {e}", exc_info=True)
            return None
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dictionary of key-value pairs
        """
        if not self.initialized or not keys:
            return {}
            
        try:
            values = await self.redis.mget(keys)
            result = {}
            
            for key, value in zip(keys, values):
                if value is not None:
                    result[key] = json.loads(value)
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting multiple values from cache: {e}", exc_info=True)
            return {}
    
    async def set_many(self, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Set multiple values in cache
        
        Args:
            data: Dictionary of key-value pairs
            ttl: Time to live in seconds
            
        Returns:
            True if successful, False otherwise
        """
        if not self.initialized or not data:
            return False
            
        try:
            # Serialize all values
            pipe = self.redis.pipeline()
            for key, value in data.items():
                serialized = json.dumps(value)
                pipe.set(key, serialized, ex=(ttl or settings.CACHE_TTL))
            
            await pipe.execute()
            return True
            
        except Exception as e:
            logger.error(f"Error setting multiple values in cache: {e}", exc_info=True)
            return False
    
    # Specialized cache methods for honeypot detector
    
    async def cache_analysis(self, contract_address: str, chain_id: int, results: Dict[str, Any]) -> bool:
        """
        Cache analysis results
        
        Args:
            contract_address: Contract address
            chain_id: Blockchain network ID
            results: Analysis results
            
        Returns:
            True if cached successfully
        """
        key = f"analysis:{chain_id}:{contract_address.lower()}"
        return await self.set(key, results)
    
    async def get_cached_analysis(self, contract_address: str, chain_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached analysis results
        
        Args:
            contract_address: Contract address
            chain_id: Blockchain network ID
            
        Returns:
            Cached analysis results or None
        """
        key = f"analysis:{chain_id}:{contract_address.lower()}"
        return await self.get(key)
    
    async def cache_contract_data(self, contract_address: str, chain_id: int, data: Dict[str, Any]) -> bool:
        """
        Cache contract data
        
        Args:
            contract_address: Contract address
            chain_id: Blockchain network ID
            data: Contract data
            
        Returns:
            True if cached successfully
        """
        key = f"contract:{chain_id}:{contract_address.lower()}"
        
        # Use longer TTL for contract data (24 hours)
        ttl = 86400
        return await self.set(key, data, ttl)
    
    async def get_cached_contract_data(self, contract_address: str, chain_id: int) -> Optional[Dict[str, Any]]:
        """
        Get cached contract data
        
        Args:
            contract_address: Contract address
            chain_id: Blockchain network ID
            
        Returns:
            Cached contract data or None
        """
        key = f"contract:{chain_id}:{contract_address.lower()}"
        return await self.get(key)
    
    async def track_rate_limit(self, client_id: str, limit: int, window: int) -> Tuple[int, bool]:
        """
        Track request rate for rate limiting
        
        Args:
            client_id: Client identifier
            limit: Maximum requests allowed
            window: Time window in seconds
            
        Returns:
            Tuple of (current count, is allowed)
        """
        key = f"ratelimit:{client_id}"
        count = await self.increment(key, 1, window)
        
        if count is None:  # Redis error
            return 0, True  # Allow request on error
            
        return count, count <= limit
    
    async def is_rate_limited(self, client_id: str) -> bool:
        """
        Check if client is currently rate limited
        
        Args:
            client_id: Client identifier
            
        Returns:
            True if rate limited
        """
        key = f"ratelimit:blocked:{client_id}"
        return await self.exists(key)
    
    async def block_client(self, client_id: str, duration: int) -> bool:
        """
        Block client for specified duration
        
        Args:
            client_id: Client identifier
            duration: Block duration in seconds
            
        Returns:
            True if successful
        """
        key = f"ratelimit:blocked:{client_id}"
        return await self.set(key, True, duration)
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get cached statistics
        
        Returns:
            Statistics data or empty dict
        """
        return await self.get("statistics") or {}
    
    async def update_statistics(self, statistics: Dict[str, Any]) -> bool:
        """
        Update cached statistics
        
        Args:
            statistics: Statistics data
            
        Returns:
            True if successful
        """
        return await self.set("statistics", statistics)

# Create singleton instance
cache_service = CacheService()


# Context manager for auto-initialization
class CacheContext:
    """Context manager for cache service"""
    
    async def __aenter__(self):
        """Initialize cache on enter"""
        await cache_service.initialize()
        return cache_service
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close cache on exit"""
        await cache_service.close()


# Import fixed
from typing import Tuple
