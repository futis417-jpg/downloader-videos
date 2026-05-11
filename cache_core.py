import json
import time
from typing import Optional, Any
from config import settings
from logger_core import logger

# [2] REDIS INTEGRATION - Caché y Rate Limiting distribuido
class RedisCache:
    """Caché distribuido con Redis (fallback a memoria si no está disponible)."""
    def __init__(self, use_redis: bool = False, url: str = "redis://localhost:6379/0"):
        self.use_redis = use_redis
        self._redis = None
        self._memory_cache = {}
        
        if use_redis:
            try:
                import redis
                self._redis = redis.from_url(url, decode_responses=True)
                self._redis.ping()
                logger.info("✅ Redis conectado. Caché y rate limiting distribuido activado.")
            except Exception as e:
                logger.warning(f"⚠️ Redis no disponible, usando caché en memoria: {e}")
                self.use_redis = False
    
    def get(self, key: str) -> Optional[Any]:
        if self.use_redis and self._redis:
            val = self._redis.get(key)
            return json.loads(val) if val else None
        return self._memory_cache.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        if self.use_redis and self._redis:
            self._redis.setex(key, ttl, json.dumps(value))
        else:
            self._memory_cache[key] = value
    
    def delete(self, key: str):
        if self.use_redis and self._redis:
            self._redis.delete(key)
        elif key in self._memory_cache:
            del self._memory_cache[key]
    
    def exists(self, key: str) -> bool:
        if self.use_redis and self._redis:
            return self._redis.exists(key)
        return key in self._memory_cache

redis_cache = RedisCache(use_redis=settings.use_redis, url=settings.redis_url)
API_RATE_LIMITS = {}

def check_api_rate_limit(ip_address: str, limit: int = 10, window: int = 60) -> bool:
    """Rate limiting con soporte Redis para distribución."""
    now = time.time()
    key = f"rate:{ip_address}"
    
    if redis_cache.use_redis:
        count = redis_cache._redis.zcard(key)
        if count >= limit:
            return True
        redis_cache._redis.zadd(key, {str(now): now})
        redis_cache._redis.zremrangebyscore(key, 0, now - window)
        return False
    else:
        if ip_address not in API_RATE_LIMITS:
            API_RATE_LIMITS[ip_address] = [now]
            return False
        API_RATE_LIMITS[ip_address] = [t for t in API_RATE_LIMITS[ip_address] if now - t < window]
        if len(API_RATE_LIMITS[ip_address]) >= limit:
            return True
        API_RATE_LIMITS[ip_address].append(now)
        return False
