"""
Rate Limiter

Token bucket algorithm implementation for API rate limiting.
Supports per-provider rate limits and distributed rate limiting with Redis.

Token Bucket Algorithm:
- A "bucket" holds tokens up to a maximum capacity (burst_size)
- Tokens are added to the bucket at a fixed rate (refill_rate)
- Each API request consumes one or more tokens
- If no tokens available, request must wait or fail
- Allows bursts up to burst_size, then throttles to refill_rate

Example:
    >>> limiter = RateLimiter(requests_per_minute=10)
    >>> if limiter.acquire():
    ...     # Make API request
    ...     pass
"""

import time
import threading
import logging
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


# Common rate limit header names used by different API providers
RATE_LIMIT_HEADERS = {
    "standard": {
        "limit": ["X-RateLimit-Limit", "X-Rate-Limit-Limit"],
        "remaining": ["X-RateLimit-Remaining", "X-Rate-Limit-Remaining"],
        "reset": ["X-RateLimit-Reset", "X-Rate-Limit-Reset"],
        "retry_after": ["Retry-After"],
    },
    "football-data": {
        "limit": ["X-RequestCounter-Limit"],
        "remaining": ["X-Requests-Available"],
        "reset": ["X-RequestCounter-Reset"],
    },
    "api-football": {
        "limit": ["X-RateLimit-Requests-Limit"],
        "remaining": ["X-RateLimit-Requests-Remaining"],
        "reset": ["X-RateLimit-Reset"],
    },
}


def parse_rate_limit_headers(
    headers: Dict[str, Any],
    provider: str = "standard"
) -> Dict[str, Optional[int]]:
    """
    Parse rate limit information from HTTP response headers.
    
    Supports multiple header naming conventions used by different API providers.
    
    Args:
        headers: HTTP response headers (case-insensitive dict)
        provider: Provider name for header mapping (default: 'standard')
                  Options: 'standard', 'football-data', 'api-football'
    
    Returns:
        Dictionary with parsed rate limit info:
        {
            'limit': Total rate limit (requests per period),
            'remaining': Remaining requests in current period,
            'reset': Unix timestamp when limit resets,
            'retry_after': Seconds to wait before retrying (if rate limited)
        }
    
    Example:
        >>> headers = {
        ...     'X-RateLimit-Limit': '60',
        ...     'X-RateLimit-Remaining': '59',
        ...     'X-RateLimit-Reset': '1704067200'
        ... }
        >>> info = parse_rate_limit_headers(headers)
        >>> print(info)
        {'limit': 60, 'remaining': 59, 'reset': 1704067200, 'retry_after': None}
    """
    # Case-insensitive header lookup
    headers_lower = {k.lower(): v for k, v in headers.items()}
    
    # Get header mappings for provider
    header_mapping = RATE_LIMIT_HEADERS.get(provider, RATE_LIMIT_HEADERS["standard"])
    
    result = {
        "limit": None,
        "remaining": None,
        "reset": None,
        "retry_after": None,
    }
    
    # Parse each rate limit component
    for key, possible_headers in header_mapping.items():
        for header_name in possible_headers:
            value = headers_lower.get(header_name.lower())
            if value is not None:
                try:
                    result[key] = int(value)
                    break
                except (ValueError, TypeError):
                    logger.warning(
                        f"Failed to parse {header_name}={value} as integer"
                    )
    
    logger.debug(f"Parsed rate limit headers ({provider}): {result}")
    return result


class RateLimiter:
    """
    Token bucket rate limiter for API requests.
    
    Thread-safe implementation that can be used across multiple threads.
    Supports both immediate acquisition and waiting for tokens.
    
    Attributes:
        requests_per_minute: Maximum requests allowed per minute
        burst_size: Maximum tokens that can accumulate (burst capacity)
        tokens: Current number of available tokens
        last_refill: Timestamp of last token refill
        provider: Provider name for header parsing (optional)
    """
    
    def __init__(
        self,
        requests_per_minute: int,
        burst_size: Optional[int] = None,
        distributed: bool = False,
        redis_client = None,
        key_prefix: str = "rate_limit",
        provider: str = "standard",
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size (defaults to requests_per_minute)
            distributed: Use Redis for distributed rate limiting (default: False)
            redis_client: Redis client instance (required if distributed=True)
            key_prefix: Redis key prefix for distributed limiting
            provider: Provider name for header parsing (default: 'standard')
            
        Example:
            >>> # Local rate limiter (10 requests/minute, burst of 10)
            >>> limiter = RateLimiter(requests_per_minute=10)
            
            >>> # Allow higher burst (10 req/min, but can burst to 20)
            >>> limiter = RateLimiter(requests_per_minute=10, burst_size=20)
            
            >>> # Distributed rate limiter with Redis
            >>> limiter = RateLimiter(
            ...     requests_per_minute=10,
            ...     distributed=True,
            ...     redis_client=redis.Redis()
            ... )
            
            >>> # Football-Data.org rate limiter
            >>> limiter = RateLimiter(
            ...     requests_per_minute=10,
            ...     provider='football-data'
            ... )
        """
        self.requests_per_minute = requests_per_minute
        self.burst_size = burst_size or requests_per_minute
        self.distributed = distributed
        self.redis_client = redis_client
        self.key_prefix = key_prefix
        self.provider = provider
        
        # Local state (used for non-distributed mode)
        self.tokens = float(self.burst_size)
        self.last_refill = time.time()
        
        # Thread lock for thread-safe operations
        self._lock = threading.Lock()
        
        # Validation
        if self.distributed and not self.redis_client:
            raise ValueError("redis_client is required when distributed=True")
        
        logger.info(
            f"Initialized RateLimiter: {requests_per_minute} req/min, "
            f"burst={self.burst_size}, distributed={distributed}, provider={provider}"
        )
    
    def _refill_tokens(self) -> None:
        """
        Refill tokens based on elapsed time since last refill.
        
        Token refill rate = requests_per_minute / 60 tokens per second
        """
        now = time.time()
        elapsed = now - self.last_refill
        
        # Calculate tokens to add based on elapsed time
        # refill_rate = tokens per second
        refill_rate = self.requests_per_minute / 60.0
        tokens_to_add = elapsed * refill_rate
        
        # Add tokens but don't exceed burst_size
        self.tokens = min(self.burst_size, self.tokens + tokens_to_add)
        self.last_refill = now
        
        logger.debug(
            f"Refilled tokens: +{tokens_to_add:.2f} → {self.tokens:.2f}/{self.burst_size}"
        )
    
    def acquire(self, tokens: int = 1, blocking: bool = False) -> bool:
        """
        Attempt to acquire tokens from the bucket.
        
        Args:
            tokens: Number of tokens to acquire (default: 1)
            blocking: If True, wait until tokens are available (default: False)
            
        Returns:
            True if tokens were acquired, False if not available
            
        Example:
            >>> limiter = RateLimiter(requests_per_minute=10)
            >>> if limiter.acquire():
            ...     print("Token acquired, making request")
            ... else:
            ...     print("Rate limit exceeded, cannot make request")
        """
        if self.distributed:
            return self._acquire_distributed(tokens, blocking)
        
        return self._acquire_local(tokens, blocking)
    
    def _acquire_local(self, tokens: int, blocking: bool) -> bool:
        """Acquire tokens using local state (non-distributed)."""
        with self._lock:
            # Refill tokens based on elapsed time
            self._refill_tokens()
            
            # Check if enough tokens available
            if self.tokens >= tokens:
                self.tokens -= tokens
                logger.debug(f"Acquired {tokens} tokens, remaining: {self.tokens:.2f}")
                return True
            
            # Not enough tokens
            if not blocking:
                logger.warning(
                    f"Rate limit exceeded: need {tokens}, have {self.tokens:.2f}"
                )
                return False
            
            # Blocking mode: calculate wait time
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / (self.requests_per_minute / 60.0)
        
        # Wait outside the lock to allow other threads
        logger.info(f"Rate limited, waiting {wait_time:.2f}s for {tokens} tokens")
        time.sleep(wait_time)
        
        # Try again after waiting
        with self._lock:
            self._refill_tokens()
            if self.tokens >= tokens:
                self.tokens -= tokens
                logger.debug(f"Acquired {tokens} tokens after waiting")
                return True
        
        return False
    
    def _acquire_distributed(self, tokens: int, blocking: bool) -> bool:
        """
        Acquire tokens using Redis (distributed rate limiting).
        
        This allows multiple processes/servers to share the same rate limit.
        Uses Redis transactions to ensure atomicity.
        """
        # TODO: Implement Redis-based distributed rate limiting
        # This is optional and can be added later when needed
        raise NotImplementedError(
            "Distributed rate limiting not yet implemented. "
            "Use distributed=False for local rate limiting."
        )
    
    def update_from_headers(self, headers: Dict[str, Any]) -> bool:
        """
        Update rate limiter state from API response headers.
        
        This allows the rate limiter to sync with the server's view of rate limits.
        Useful when the API provides accurate remaining request counts.
        
        Args:
            headers: HTTP response headers
            
        Returns:
            True if headers were parsed and state updated, False otherwise
            
        Example:
            >>> limiter = RateLimiter(requests_per_minute=10, provider='football-data')
            >>> response = requests.get('https://api.football-data.org/v4/teams')
            >>> limiter.update_from_headers(response.headers)
            >>> print(f"Tokens remaining: {limiter.get_available_tokens()}")
        """
        if self.distributed:
            logger.warning("update_from_headers not supported in distributed mode")
            return False
        
        # Parse headers
        rate_info = parse_rate_limit_headers(headers, provider=self.provider)
        
        # Update state if we got useful information
        updated = False
        
        with self._lock:
            # Update remaining tokens if available
            if rate_info["remaining"] is not None:
                old_tokens = self.tokens
                self.tokens = float(rate_info["remaining"])
                
                # Don't exceed burst size
                self.tokens = min(self.tokens, self.burst_size)
                
                logger.info(
                    f"Updated tokens from headers: {old_tokens:.2f} → {self.tokens:.2f} "
                    f"(remaining: {rate_info['remaining']})"
                )
                updated = True
            
            # Update last_refill time to avoid double counting
            if updated:
                self.last_refill = time.time()
            
            # Log other useful info
            if rate_info["limit"] is not None:
                logger.debug(f"API reports rate limit: {rate_info['limit']}")
            
            if rate_info["reset"] is not None:
                reset_time = datetime.fromtimestamp(rate_info["reset"])
                logger.debug(f"Rate limit resets at: {reset_time}")
            
            if rate_info["retry_after"] is not None:
                logger.warning(
                    f"API requests to wait {rate_info['retry_after']}s before retry"
                )
        
        return updated
    
    def wait_if_needed(self, tokens: int = 1) -> float:
        """
        Wait if necessary to acquire tokens (blocking call).
        
        This is equivalent to acquire(tokens, blocking=True) but returns
        the actual wait time.
        
        Args:
            tokens: Number of tokens to acquire
            
        Returns:
            Time waited in seconds (0 if no wait was needed)
            
        Example:
            >>> limiter = RateLimiter(requests_per_minute=10)
            >>> wait_time = limiter.wait_if_needed()
            >>> print(f"Waited {wait_time:.2f}s before making request")
        """
        start_time = time.time()
        self.acquire(tokens, blocking=True)
        wait_time = time.time() - start_time
        
        if wait_time > 0.01:  # Only log if meaningful wait
            logger.info(f"Waited {wait_time:.2f}s for rate limit")
        
        return wait_time
    
    def get_available_tokens(self) -> float:
        """
        Get current number of available tokens.
        
        Returns:
            Number of tokens currently available (may be fractional)
        """
        if self.distributed:
            raise NotImplementedError(
                "get_available_tokens not supported in distributed mode"
            )
        
        with self._lock:
            self._refill_tokens()
            return self.tokens
    
    def get_wait_time(self, tokens: int = 1) -> float:
        """
        Calculate time to wait until tokens are available.
        
        Args:
            tokens: Number of tokens needed
            
        Returns:
            Time to wait in seconds (0 if tokens already available)
            
        Example:
            >>> limiter = RateLimiter(requests_per_minute=10)
            >>> wait_time = limiter.get_wait_time()
            >>> if wait_time > 0:
            ...     print(f"Need to wait {wait_time:.2f}s")
        """
        if self.distributed:
            raise NotImplementedError(
                "get_wait_time not supported in distributed mode"
            )
        
        with self._lock:
            self._refill_tokens()
            
            if self.tokens >= tokens:
                return 0.0
            
            tokens_needed = tokens - self.tokens
            wait_time = tokens_needed / (self.requests_per_minute / 60.0)
            return wait_time
    
    def reset(self) -> None:
        """
        Reset the rate limiter to full capacity.
        
        Useful for testing or manual resets.
        """
        if self.distributed:
            raise NotImplementedError("reset not supported in distributed mode")
        
        with self._lock:
            self.tokens = float(self.burst_size)
            self.last_refill = time.time()
            logger.info("Rate limiter reset to full capacity")
    
    def __repr__(self) -> str:
        """String representation of rate limiter."""
        return (
            f"RateLimiter(requests_per_minute={self.requests_per_minute}, "
            f"burst_size={self.burst_size}, "
            f"tokens={self.tokens:.2f}, "
            f"distributed={self.distributed}, "
            f"provider={self.provider})"
        )


class RateLimiterRegistry:
    """
    Registry for managing multiple rate limiters by provider.
    
    Allows easy access to provider-specific rate limiters.
    
    Example:
        >>> registry = RateLimiterRegistry()
        >>> registry.register('football-data', requests_per_minute=10, provider='football-data')
        >>> registry.register('api-football', requests_per_minute=100, burst_size=10, provider='api-football')
        >>> 
        >>> limiter = registry.get('football-data')
        >>> if limiter.acquire():
        ...     # Make API request
        ...     response = requests.get(...)
        ...     limiter.update_from_headers(response.headers)
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = threading.Lock()
    
    def register(
        self,
        provider: str,
        requests_per_minute: int,
        burst_size: Optional[int] = None,
        **kwargs
    ) -> RateLimiter:
        """
        Register a rate limiter for a provider.
        
        Args:
            provider: Provider name (e.g., 'football-data', 'api-football')
            requests_per_minute: Maximum requests per minute
            burst_size: Maximum burst size
            **kwargs: Additional arguments for RateLimiter (including provider for header parsing)
            
        Returns:
            The registered RateLimiter instance
        """
        with self._lock:
            if provider in self._limiters:
                logger.warning(f"Rate limiter for '{provider}' already exists, replacing")
            
            # If provider arg not in kwargs, use the registry key as provider
            if 'provider' not in kwargs:
                kwargs['provider'] = provider
            
            limiter = RateLimiter(
                requests_per_minute=requests_per_minute,
                burst_size=burst_size,
                **kwargs
            )
            self._limiters[provider] = limiter
            
            logger.info(f"Registered rate limiter for '{provider}'")
            return limiter
    
    def get(self, provider: str) -> Optional[RateLimiter]:
        """
        Get rate limiter for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            RateLimiter instance or None if not registered
        """
        return self._limiters.get(provider)
    
    def get_or_create(
        self,
        provider: str,
        requests_per_minute: int,
        burst_size: Optional[int] = None,
        **kwargs
    ) -> RateLimiter:
        """
        Get existing rate limiter or create new one.
        
        Args:
            provider: Provider name
            requests_per_minute: Maximum requests per minute (used if creating)
            burst_size: Maximum burst size (used if creating)
            **kwargs: Additional arguments for RateLimiter
            
        Returns:
            RateLimiter instance
        """
        limiter = self.get(provider)
        if limiter is None:
            limiter = self.register(
                provider,
                requests_per_minute,
                burst_size,
                **kwargs
            )
        return limiter
    
    def list_providers(self) -> list[str]:
        """Get list of registered providers."""
        return list(self._limiters.keys())
    
    def remove(self, provider: str) -> bool:
        """
        Remove rate limiter for a provider.
        
        Args:
            provider: Provider name
            
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            if provider in self._limiters:
                del self._limiters[provider]
                logger.info(f"Removed rate limiter for '{provider}'")
                return True
            return False
