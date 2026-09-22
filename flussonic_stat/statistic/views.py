import time
import asyncio
import httpx
import logging
from collections import defaultdict
from asgiref.sync import sync_to_async

from django.conf import settings
from django.core.cache import cache
from django.db import transaction

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from config.models import ServerModel
from notify_session.models import StatusSessionModel
from statistic.serializers import SessionSerializer
from utils.is_memcached_available import is_memcached_available
from utils.safe_cache import safe_cache_set, safe_cache_get, safe_cache_get_many

from utils.tg_send_message import send_message_to_tg

logger = logging.getLogger(__name__)

GLOBAL_TOKENS_KEY = "active_tokens_registry"
CACHE_TTL = 172800  # 48 hours


def register_active_tokens(new_tokens: set):
    try:
        now = int(time.time())
        cutoff = now - CACHE_TTL

        registry = safe_cache_get(GLOBAL_TOKENS_KEY, {}) or {}
        registry = {tok: seen for tok, seen in registry.items() if seen >= cutoff}

        for tok in new_tokens:
            registry[tok] = now

        safe_cache_set(GLOBAL_TOKENS_KEY, registry, timeout=CACHE_TTL)
    except Exception as e:
        logger.warning(f"Failed to register active tokens: {e}")


def get_active_tokens() -> list:
    try:
        now = int(time.time())
        cutoff = now - CACHE_TTL
        registry = safe_cache_get(GLOBAL_TOKENS_KEY, {}) or {}
        return [tok for tok, seen in registry.items() if seen >= cutoff]
    except Exception as e:
        logger.warning(f"Failed to get active tokens: {e}")
        return []


def get_latest_tokens_summary():
    latest_ts = cache.get("latest_base_unix_time")
    if not latest_ts:
        return None, []

    active_tokens = get_active_tokens()
    if not active_tokens:
        return latest_ts, []

    key_to_token = {f"{token}:{latest_ts}": token for token in active_tokens}
    cached_data = cache.get_many(list(key_to_token.keys()))

    results = []
    for key, token in key_to_token.items():
        items = cached_data.get(key)
        if items:
            total_count = sum(i.get("count", 0) for i in items)

            if total_count < 2:
                continue

            results.append({
                "token": token,
                "total_count": total_count,
                "users_count": len(items),
                "users": items
            })

    results.sort(key=lambda x: x["total_count"], reverse=True)

    return latest_ts, results


class AllSessionsUserView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        latest_ts, records = get_latest_tokens_summary()

        if latest_ts is None:
            return Response(
                {"detail": "No cached data found yet."},
                status=status.HTTP_404_NOT_FOUND
            )

        response_data = {
            "base_unix_time": latest_ts,
            "total_active_tokens": len(records),
            "tokens": records
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TokenSessionsUserView(APIView):
    renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        token = kwargs.get("pk")

        if not token:
            return Response(
                {"detail": "Token is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = int(time.time())
        base_unix_time = now // 60 * 60 * 1000  # current minute bucket, ms

        date_list = [base_unix_time - x * 60000 for x in range(5)]
        key_to_ts = {f"{token}:{ts}": ts for ts in date_list}

        cached_records = safe_cache_get_many(list(key_to_ts.keys()))

        per_minute = []
        aggregated_users = defaultdict(int)

        last_minute_key = f"{token}:{base_unix_time}"
        last_minute_items = cached_records.get(last_minute_key, []) if cached_records else []
        for i in last_minute_items:
            user_id = i.get("user_id")
            cnt = i.get("count", 0)
            if user_id is not None:
                aggregated_users[user_id] += cnt

        for key, ts in key_to_ts.items():
            items = cached_records.get(key, []) if cached_records else []
            minute_count = sum(i.get("count", 0) for i in items) if items else 0
            per_minute.append({"timestamp": ts, "count": minute_count})

        per_minute.sort(key=lambda row: row["timestamp"])

        users = [
            {"user_id": uid, "count": cnt}
            for uid, cnt in aggregated_users.items()
        ]
        users.sort(key=lambda u: u["count"], reverse=True)

        total_count = sum(row["count"] for row in per_minute)
        avg_per_minute = round(total_count / 5, 2)

        response_data = {
            "token": token,
            "base_unix_time": base_unix_time,
            "window_minutes": 5,
            "avg_per_minute": avg_per_minute,
            "users_count": len(users),
            "users": users,
            "per_minute": per_minute,
        }

        return Response(response_data, status=status.HTTP_200_OK)


class TokenCacheStatView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        now = int(time.time())
        base_unix_time = now // 60 * 60 * 1000
        date_list = [base_unix_time - x * 60000 for x in range(24 * 60)]
        token_or_ip = kwargs.get("pk")

        key_to_ts = {f"{token_or_ip}:{ts}": ts for ts in date_list}

        cached_records = safe_cache_get_many(list(key_to_ts.keys()))

        result = []
        for key, ts in key_to_ts.items():
            items = cached_records.get(key, []) if cached_records else []
            total_count = sum(i.get("count", 0) for i in items) if items else 0
            result.append((ts, total_count))

        result.sort(key=lambda tup: tup[0])
        return Response(result, status=status.HTTP_200_OK)


class GetStatView(APIView):
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    async def fetch_server_stats(self, client, server):

        ip = server.get('ip')
        url = server.get('url')
        endpoint = f"http://{ip}:89/{url}/sessions"
        auth = (settings.FLUSSONIC_LOGIN, settings.FLUSSONIC_PASSWORD)

        try:
            response = await client.get(endpoint, auth=auth, timeout=10.0)
            response.raise_for_status()
            res = response.json()
            return res.get('sessions') or res.get('items') or []
        except Exception as e:
            await sync_to_async(send_message_to_tg)(f"Error connecting to {ip}: {e}")
            return []

    def get(self, request, *args, **kwargs):

        base_unix_time = int(time.time() // 60 * 60 * 1000)
        list_server = list(ServerModel.objects.all().values('ip', 'url'))

        async def run_requests():
            async with httpx.AsyncClient() as client:
                tasks = [self.fetch_server_stats(client, s) for s in list_server]
                return await asyncio.gather(*tasks)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            results = loop.run_until_complete(run_requests())
        finally:
            loop.close()

        list_all_sessions = [item for sublist in results for item in sublist]

        self.process_and_save(list_all_sessions, base_unix_time)

        return Response(status=status.HTTP_200_OK)

    def process_and_save(self, list_all_sessions, base_unix_time):

        list_for_deleted = [s.get('id') for s in list_all_sessions if s.get('type') == 'play']

        filtered_sessions = [
            s for s in list_all_sessions
            if s.get('type') == 'play'
               and s.get('duration', 0) > 60000
               and s.get('token')
               and s.get('user_id')
        ]

        self.sync_cash(filtered_sessions, base_unix_time)

        incoming_ids = [s['id'] for s in filtered_sessions]

        with transaction.atomic():
            existing_sessions_dict = {
                obj.session_id: obj
                for obj in StatusSessionModel.objects.filter(session_id__in=incoming_ids)
            }

            self._create_missing_sessions(filtered_sessions, existing_sessions_dict)
            self._resurrect_mistakenly_closed_sessions(incoming_ids, existing_sessions_dict)
            self._close_expired_sessions(list_for_deleted, base_unix_time)

    def _create_missing_sessions(self, filtered_sessions, existing_sessions_dict):

        new_records = []
        for item in filtered_sessions:
            if item['id'] not in existing_sessions_dict:
                token = item.get('token', '').split('?utc=')[0]
                raw_user_agent = item.get('user_agent') or ""
                truncated_user_agent = raw_user_agent[:255]
                new_records.append(StatusSessionModel(
                    session_id=item['id'],
                    bytes_sent=item.get('bytes'),
                    country=item.get('country'),
                    created_at=item.get('opened_at'),
                    deleted_at=1,
                    ip=item.get('ip'),
                    last_access_time=item.get('opened_at'),
                    media=item.get('user_name'),
                    token=token,
                    type='mpegts' if item.get('proto') == 'tshttp' else item.get('proto'),
                    user_agent=truncated_user_agent,
                    user_id=item.get('user_id')
                ))

        if new_records:
            StatusSessionModel.objects.bulk_create(new_records)

    def _resurrect_mistakenly_closed_sessions(self, incoming_ids, existing_sessions_dict):
        ids_to_resurrect = [
            s_id for s_id in incoming_ids
            if s_id in existing_sessions_dict and existing_sessions_dict[s_id].deleted_at != 1
        ]

        if ids_to_resurrect:
            StatusSessionModel.objects.filter(session_id__in=ids_to_resurrect).update(deleted_at=1)

    def _close_expired_sessions(self, list_for_deleted, base_unix_time):
        StatusSessionModel.objects.filter(
            deleted_at=1
        ).exclude(
            session_id__in=list_for_deleted
        ).update(deleted_at=base_unix_time)

    def sync_cash(self, filtered_all_sessions, base_unix_time):

        if not is_memcached_available():
            msg = "[Memcached Down] Server is unavailable, cache synchronization skipped."
            logger.error(msg)
            try:
                send_message_to_tg(msg)
            except Exception as tg_err:
                logger.error(f"Failed to send alert to Telegram: {tg_err}")
            return

        try:
            aggregated = defaultdict(lambda: defaultdict(int))
            batch_tokens = set()

            for session in filtered_all_sessions:
                raw_token = session.get('token')
                user_id = session.get('user_id')
                if not raw_token or not user_id:
                    continue

                token = raw_token.split('?utc=')[0]
                aggregated[token][user_id] += 1
                batch_tokens.add(token)

            for token, user_counts in aggregated.items():
                key = f"{token}:{base_unix_time}"
                records = [{'user_id': uid, 'count': cnt} for uid, cnt in user_counts.items()]
                safe_cache_set(key, records, timeout=CACHE_TTL)

            cache.set("latest_base_unix_time", base_unix_time, timeout=CACHE_TTL)

            if batch_tokens:
                register_active_tokens(batch_tokens)

        except Exception as e:
            error_msg = f"⚠️ [Cache Error] Failed to sync cache: {e}"
            logger.error(error_msg)
            try:
                send_message_to_tg(error_msg)
            except Exception as tg_err:
                logger.error(f"Failed to send alert to Telegram: {tg_err}")
