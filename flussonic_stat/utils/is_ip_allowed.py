from typing import Optional

from django.core.cache import cache

from config.models import ServerModel

ALLOWED_IPS_CACHE_KEY = "allowed_server_ips"
ALLOWED_IPS_TTL = 86400

def get_server_url_by_ip(client_ip: str) -> Optional[str]:

    servers_dict = cache.get(ALLOWED_IPS_CACHE_KEY)

    if servers_dict is None:
        servers_dict = dict(ServerModel.objects.values_list('ip', 'url'))
        cache.set(ALLOWED_IPS_CACHE_KEY, servers_dict, timeout=ALLOWED_IPS_TTL)

    return servers_dict.get(client_ip)


def is_ip_allowed(client_ip: str) -> bool:

    return get_server_url_by_ip(client_ip) is not None