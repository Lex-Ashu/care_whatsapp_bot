import time
import logging
from functools import wraps
from typing import Callable, Dict, Optional, Any

logger = logging.getLogger('whatsapp_bot')

class RateLimiter:
    
    def __init__(self, refill_rate: float, bucket_size: int):
        self.refill_rate = refill_rate  # tokens per second
        self.bucket_size = bucket_size
        self.tokens = bucket_size  # start with a full bucket
        self.last_refill = time.time()
    
    def _refill(self):
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        self.tokens = min(self.bucket_size, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def consume(self, tokens: int = 1) -> bool:
        self._refill()
        if tokens <= self.tokens:
            self.tokens -= tokens
            return True
        return False
    
    def wait_for_tokens(self, tokens: int = 1) -> float:
        self._refill()
        if tokens <= self.tokens:
            self.tokens -= tokens
            return 0.0
        
        # Calculate how long to wait for enough tokens
        tokens_needed = tokens - self.tokens
        wait_time = tokens_needed / self.refill_rate
        
        logger.debug(f"Rate limit reached. Waiting for {wait_time:.2f} seconds")
        time.sleep(wait_time)
        
        self.tokens = 0
        self.last_refill = time.time()
        return wait_time

# Global rate limiters for different API endpoints
_rate_limiters: Dict[str, RateLimiter] = {
    'whatsapp_send': RateLimiter(refill_rate=5, bucket_size=10),  # 5 messages per second, burst of 10
    'whatsapp_read': RateLimiter(refill_rate=10, bucket_size=20),  # 10 read receipts per second, burst of 20
    'care_api': RateLimiter(refill_rate=2, bucket_size=5),  # 2 requests per second, burst of 5
}

def rate_limited(limiter_key: str, tokens: int = 1):
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            limiter = _rate_limiters.get(limiter_key)
            if limiter is None:
                logger.warning(f"No rate limiter found for key: {limiter_key}")
                return func(*args, **kwargs)
            
            wait_time = limiter.wait_for_tokens(tokens)
            if wait_time > 0:
                logger.info(f"Rate limited {func.__name__} for {wait_time:.2f} seconds")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator