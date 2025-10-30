"""
Cache Manager

Django cache integration for API responses.
Supports different TTL strategies for one-time vs. periodic data.
"""

import logging
from typing import Any, Optional, List
from django.core.cache import cache

logger = logging.getLogger(__name__)


class CacheManager:
    """
    Manager for caching API responses using Django cache backend.
    
    Supports multiple TTL strategies:
    - One-time fetches: 30 days (rarely changing data)
    - Periodic updates: 1 day (frequently updated data)
    - Short-lived: 1 hour (highly dynamic data)
    
    Examples:
        >>> cache_mgr = CacheManager(prefix='teams_api')
        >>> cache_mgr.set('team:123', {'name': 'Real Madrid'}, ttl=CacheManager.TTL_PERIODIC)
        >>> data = cache_mgr.get('team:123')
        >>> cache_mgr.invalidate('team:123')
    """
    
    # Default TTL values (in seconds)
    TTL_ONE_TIME = 30 * 24 * 60 * 60  # 30 days for one-time fetches
    TTL_PERIODIC = 24 * 60 * 60       # 1 day for periodic updates
    TTL_SHORT = 60 * 60                # 1 hour for frequently changing data
    
    def __init__(self, prefix: str = 'api_integration'):
        """
        Initialize cache manager.
        
        Args:
            prefix: Prefix for cache keys (e.g., 'teams_api', 'stats_api')
        """
        self.prefix = prefix
        logger.info(f"Initialized CacheManager with prefix='{prefix}'")
    
    def _make_key(self, key: str) -> str:
        """
        Generate cache key with prefix.
        
        Args:
            key: Base cache key
            
        Returns:
            Full cache key with prefix (e.g., 'teams_api:team:123')
        """
        return f"{self.prefix}:{key}"
    
    def get(self, key: str, default: Any = None) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key (without prefix)
            default: Default value if key not found
            
        Returns:
            Cached value or default if not found
            
        Examples:
            >>> cache_mgr.get('team:123')
            {'name': 'Real Madrid', 'code': 'RMA'}
            >>> cache_mgr.get('team:999', default={})
            {}
        """
        full_key = self._make_key(key)
        value = cache.get(full_key, default)
        
        if value is not None and value != default:
            logger.debug(f"Cache HIT: {full_key}")
        else:
            logger.debug(f"Cache MISS: {full_key}")
        
        return value
    
    def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = TTL_PERIODIC
    ) -> bool:
        """
        Set value in cache with TTL.
        
        Args:
            key: Cache key (without prefix)
            value: Value to cache (must be serializable)
            ttl: Time-to-live in seconds (default: 1 day)
            
        Returns:
            True if successful, False otherwise
            
        Examples:
            >>> # One-time fetch (30 days)
            >>> cache_mgr.set('team:123', team_data, ttl=CacheManager.TTL_ONE_TIME)
            
            >>> # Periodic update (1 day)
            >>> cache_mgr.set('stats:123', stats_data)  # Uses default TTL_PERIODIC
            
            >>> # Short-lived data (1 hour)
            >>> cache_mgr.set('live_score:123', score, ttl=CacheManager.TTL_SHORT)
        """
        full_key = self._make_key(key)
        
        try:
            cache.set(full_key, value, ttl)
            logger.debug(f"Cache SET: {full_key} (TTL={ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Failed to set cache key {full_key}: {e}")
            return False
    
    def invalidate(self, key: str) -> bool:
        """
        Invalidate (delete) a single cache entry.
        
        Args:
            key: Cache key (without prefix)
            
        Returns:
            True if successful, False otherwise
            
        Examples:
            >>> cache_mgr.invalidate('team:123')
            True
        """
        full_key = self._make_key(key)
        
        try:
            cache.delete(full_key)
            logger.debug(f"Cache INVALIDATE: {full_key}")
            return True
        except Exception as e:
            logger.error(f"Failed to invalidate cache key {full_key}: {e}")
            return False
    
    def invalidate_many(self, keys: List[str]) -> int:
        """
        Invalidate multiple cache entries at once.
        
        Args:
            keys: List of cache keys (without prefix)
            
        Returns:
            Number of successfully invalidated keys
            
        Examples:
            >>> cache_mgr.invalidate_many(['team:123', 'team:456', 'team:789'])
            3
        """
        full_keys = [self._make_key(key) for key in keys]
        
        try:
            cache.delete_many(full_keys)
            logger.info(f"Cache INVALIDATE MANY: {len(full_keys)} keys")
            return len(full_keys)
        except Exception as e:
            logger.error(f"Failed to invalidate multiple keys: {e}")
            return 0
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache entries matching a pattern.
        
        Note: This requires Redis backend with scan() support.
        Falls back to no-op for other backends.
        
        Args:
            pattern: Pattern to match (e.g., 'team:*', 'stats:league:*')
            
        Returns:
            Number of invalidated keys (0 if backend doesn't support)
            
        Examples:
            >>> # Invalidate all teams
            >>> cache_mgr.invalidate_pattern('team:*')
            150
            
            >>> # Invalidate stats for a specific league
            >>> cache_mgr.invalidate_pattern('stats:league:39:*')
            20
        """
        full_pattern = self._make_key(pattern)
        
        try:
            # Try to use Redis-specific functionality
            from django.core.cache.backends.redis import RedisCache
            
            if isinstance(cache, RedisCache):
                # Redis backend - use SCAN for pattern matching
                keys = []
                client = cache._cache
                
                for key in client.scan_iter(match=full_pattern):
                    keys.append(key)
                
                if keys:
                    cache.delete_many(keys)
                    logger.info(f"Cache INVALIDATE PATTERN: {full_pattern} ({len(keys)} keys)")
                    return len(keys)
                else:
                    logger.debug(f"Cache INVALIDATE PATTERN: No keys matching {full_pattern}")
                    return 0
            else:
                logger.warning(
                    f"Pattern invalidation not supported for {type(cache).__name__}. "
                    "Use Redis backend for this feature."
                )
                return 0
                
        except ImportError:
            logger.warning("Redis backend not available. Pattern invalidation skipped.")
            return 0
        except Exception as e:
            logger.error(f"Failed to invalidate pattern {full_pattern}: {e}")
            return 0
    
    def clear_all(self) -> bool:
        """
        Clear all cache entries for this prefix.
        
        Warning: This will delete ALL cached data for this prefix!
        
        Returns:
            True if successful, False otherwise
            
        Examples:
            >>> cache_mgr.clear_all()  # Clear all 'teams_api:*' entries
            True
        """
        try:
            # Try pattern-based deletion first (Redis only)
            count = self.invalidate_pattern('*')
            
            if count > 0:
                logger.warning(f"Cache CLEAR ALL: Deleted {count} keys with prefix '{self.prefix}'")
                return True
            else:
                # Fallback: clear entire cache (affects all apps!)
                logger.warning(
                    f"Pattern deletion failed. Consider using Redis backend or "
                    f"manually clearing cache for prefix '{self.prefix}'"
                )
                return False
                
        except Exception as e:
            logger.error(f"Failed to clear cache: {e}")
            return False
    
    def get_or_set(
        self,
        key: str,
        default_fn: callable,
        ttl: int = TTL_PERIODIC
    ) -> Any:
        """
        Get value from cache, or compute and cache it if missing.
        
        Args:
            key: Cache key (without prefix)
            default_fn: Function to call if cache miss (must return serializable value)
            ttl: Time-to-live in seconds (default: 1 day)
            
        Returns:
            Cached value or newly computed value
            
        Examples:
            >>> def fetch_team():
            ...     return api_client.get_team(123)
            ...
            >>> team = cache_mgr.get_or_set('team:123', fetch_team, ttl=CacheManager.TTL_ONE_TIME)
        """
        # Try to get from cache first
        value = self.get(key)
        
        if value is not None:
            return value
        
        # Cache miss - compute value
        try:
            value = default_fn()
            self.set(key, value, ttl)
            return value
        except Exception as e:
            logger.error(f"Failed to compute value for key {key}: {e}")
            raise


# Convenience function for quick cache operations
def get_cache_manager(prefix: str = 'api_integration') -> CacheManager:
    """
    Factory function to get a cache manager instance.
    
    Args:
        prefix: Cache key prefix
        
    Returns:
        CacheManager instance
        
    Examples:
        >>> from api_integrations.base import get_cache_manager
        >>> cache = get_cache_manager('teams_api')
        >>> cache.set('team:123', team_data)
    """
    return CacheManager(prefix=prefix)
