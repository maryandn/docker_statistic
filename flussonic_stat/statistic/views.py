import time
import asyncio
import httpx
from itertools import groupby
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

from utils.tg_send_message import send_message_to_tg


def canonicalize_dict(x):
    return sorted(
        ((k, '' if v is None else v) for k, v in x.items()),
        key=lambda x: hash(x[0])
    )


def unique_and_count(lst):
    grouper = groupby(sorted(map(canonicalize_dict, lst)))
    return [dict(k + [("count", len(list(g)))]) for k, g in grouper]


class TokenCacheStatView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        now = int(time.time())
        base_unix_time = now // 60 * 60 * 1000

        date_list = [base_unix_time - x * 60000 for x in range(24 * 60)]

        token_or_ip = kwargs.get("pk")

        result = []
        for ts in date_list:
            key = f"{token_or_ip}:{ts}"
            items = cache.get(key, [])
            if not items:
                result.append((ts, 0))
            else:
                total_count = sum(i.get("count", 0) for i in items)
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
        list_for_count = []

        for session in filtered_all_sessions:
            data_dict_items = {
                'ip': session.get('ip'),
                'token': session.get('token', ''),
                'name': session.get('name'),
                'user_id': session.get('user_id', ''),
                'session_id': session.get('id')
            }
            list_for_count.append(data_dict_items)

        data = unique_and_count(list_for_count)

        for item in data:
            token = item.get("token")
            if not token:
                continue
            key = f"{token}:{base_unix_time}"
            existing = cache.get(key, [])
            existing.append(item)

            cache.set(key, existing, timeout=172800)
