import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)

def is_memcached_available() -> bool:
    try:
        ping_key = "__healthcheck_ping__"
        cache.set(ping_key, "pong", timeout=10)
        result = cache.get(ping_key)
        return result == "pong"
    except Exception as e:
        logger.warning(f"Healthcheck error: {e}")
        return False