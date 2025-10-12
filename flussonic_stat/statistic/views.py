from django.conf import settings
from django.core.cache import cache

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from config.models import ServerModel
from notify_session.models import StatusSessionModel
from statistic.serializers import SessionSerializer

import requests
from itertools import groupby
import time

from utils.tg_send_message import send_message_to_tg


def canonicalize_dict(x):
    return sorted(x.items(), key=lambda x: hash(x[0]))


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

    def get(self, request, *args, **kwargs):

        base_unix_time = int(time.time() // 60 * 60 * 1000)
        list_server = ServerModel.objects.all().values('ip', 'url')

        list_all_sessions = []
        list_for_count = []
        list_for_deleted = []

        for server in list_server:
            ip = server.get('ip')
            url = server.get('url')
            try:
                res = requests.get(
                    f'http://{settings.FLUSSONIC_LOGIN}:{settings.FLUSSONIC_PASSWORD}@{ip}:89/{url}/sessions',
                    timeout=5)
                res.raise_for_status()
                res = res.json()
                if res.get('sessions', False):
                    list_all_sessions.extend(res['sessions'])
                elif res.get('items', False):
                    list_all_sessions.extend(res['items'])
            except requests.ConnectionError as e:
                send_message_to_tg(f"Error ConnectionError {ip}: {e}")
                continue
            except requests.Timeout as e:
                send_message_to_tg(f"Error Timeout {ip}: {e}")
                continue
            except requests.RequestException as e:
                send_message_to_tg(f"Error RequestException {ip}: {e}")
                continue

        filtered_all_sessions = [session for session in list_all_sessions if
                                 session.get('type') == 'play' and session.get('duration', 0) > 60000]

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

        incoming_ids = [item['id'] for item in filtered_all_sessions]
        existing_ids = set(
            StatusSessionModel.objects.filter(deleted_at=1, session_id__in=incoming_ids)
            .values_list('session_id', flat=True))

        new_objects = []

        for item in filtered_all_sessions:
            if item['id'] not in existing_ids:
                new_objects.append(StatusSessionModel(
                    bytes_sent=item.get('bytes'),
                    country=item.get('country'),
                    created_at=item.get('opened_at'),
                    deleted_at=1,
                    ip=item.get('ip'),
                    last_access_time=item.get('opened_at'),
                    media=item.get('user_name'),
                    session_id=item.get('id'),
                    token=item.get('token'),
                    type='mpegts' if item.get('proto') == 'tshttp' else item.get('proto'),
                    user_agent=item.get('user_agent'),
                    user_id=item.get('user_id')
                ))

        if new_objects:
            StatusSessionModel.objects.bulk_create(new_objects)

        no_deleted = list(StatusSessionModel.objects.filter(deleted_at=1).values_list('session_id', flat=True))

        res_for_deleted_at = list(set(no_deleted) - set(list_for_deleted))

        StatusSessionModel.objects.filter(session_id__in=res_for_deleted_at).update(deleted_at=base_unix_time)

        return Response(status=status.HTTP_200_OK)
