import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

CACHE_TTL = 172800

def safe_cache_get(key, default=None):
    try:
        return cache.get(key, default)
    except Exception as e:
        logger.warning(f"Cache get error for key '{key}': {e}")
        return default


def safe_cache_set(key, value, timeout=CACHE_TTL):
    try:
        cache.set(key, value, timeout=timeout)
    except Exception as e:
        logger.warning(f"Cache set error for key '{key}': {e}")


def safe_cache_get_many(keys):
    try:
        return cache.get_many(keys)
    except Exception as e:
        logger.warning(f"Cache get_many error for {len(keys)} keys: {e}")
        return {}