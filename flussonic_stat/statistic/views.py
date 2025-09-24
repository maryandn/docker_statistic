from collections import defaultdict

from django.db.models import Sum
from django.conf import settings
from django.core.cache import cache

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from config.models import ServerModel
from notify_session.models import StatusSessionModel
from statistic.models import SessionModel
from statistic.serializers import SessionSerializer

import requests
from itertools import groupby
import datetime
import time

from utils.tg_send_message import send_message_to_tg


def canonicalize_dict(x):
    return sorted(x.items(), key=lambda x: hash(x[0]))


def unique_and_count(lst):
    grouper = groupby(sorted(map(canonicalize_dict, lst)))
    return [dict(k + [("count", len(list(g)))]) for k, g in grouper]


class TokenMysqlStatView(generics.ListAPIView):
    renderer_classes = [JSONRenderer]
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        base_unix_time = int(datetime.datetime.now().strftime('%s')) // 60 * 60 * 1000
        date_list = [base_unix_time - x * 60000 for x in range(24 * 60)]

        result = SessionModel.objects.filter(time__in=date_list)
        return result

    def get(self, request, *args, **kwargs):
        base_unix_time = int(datetime.datetime.now().strftime('%s')) // 60 * 60 * 1000
        date_list = [base_unix_time - x * 60000 for x in range(24 * 60)]

        qs = self.get_queryset()
        token_or_ip = kwargs.get('pk')

        if token_or_ip.count('.') == 3 and all(0 <= int(num) < 256 for num in token_or_ip.rstrip().split('.')):
            result = qs.filter(ip=token_or_ip).values_list('time').annotate(
                count=Sum('count')).order_by('time')

            diff = list(set(date_list) - set([i[0] for i in list(result)]))
            result = list(result)

            for i in diff:
                result.append((i, 0))

            result.sort(key=lambda tup: tup[0])

        else:
            result = qs.filter(token=token_or_ip).values_list('time').annotate(
                count=Sum('count')).order_by('time')

            diff = list(set(date_list) - set([i[0] for i in list(result)]))
            result = list(result)

            for i in diff:
                result.append((i, 0))

            result.sort(key=lambda tup: tup[0])

        return Response(result, status.HTTP_200_OK)


class TokenCacheStatView(APIView):
    renderer_classes = [JSONRenderer]
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        now = int(time.time())
        base_unix_time = now // 60 * 60 * 1000

        date_list = [base_unix_time - x * 60000 for x in range(24 * 60)]

        token_or_ip = kwargs.get("pk")
        data = cache.get(token_or_ip, {})

        result = []
        for ts in date_list:
            items = data.get(ts, [])
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

        now_ms = int(time.time() * 1000)
        base_unix_time = (now_ms // 60000) * 60000
        date_for_del = base_unix_time - 172800000

        list_server = ServerModel.objects.all().values('ip', 'url')

        dict_for_count = []
        dict_for_deleted = []

        for server in list_server:
            try:
                ip = server.get('ip')
                url = server.get('url')
                res = requests.get(
                    f'http://{settings.FLUSSONIC_LOGIN}:{settings.FLUSSONIC_PASSWORD}@{ip}:89/{url}/sessions',
                    timeout=5)
                res.raise_for_status()
                res = res.json()
                if res.get('sessions', False):
                    for i in res.get('sessions'):
                        if i.get('type') == 'play':
                            current_unix_time_ms = int(time.time() * 1000)
                            duration = current_unix_time_ms - i.get('opened_at')
                            if duration > 60000:
                                data_dict_sessions = {
                                    'source': f'{ip}',
                                    'ip': i.get('ip'),
                                    'token': i.get('token') if i.get('token') else '',
                                    'name': i.get('name'),
                                    'user_id': i.get('user_id') if i.get('user_id') else '',
                                    'session_id': i.get('id')
                                }
                                dict_for_count.append(data_dict_sessions)

                            dict_for_deleted.append(i.get('id'))

                elif res.get('items', False):

                    for i in res.get('items'):
                        if i.get('type') == 'play':
                            if i.get('duration') > 60000:
                                data_dict_items = {
                                    'source': f'{ip}',
                                    'ip': i.get('ip'),
                                    'token': i.get('token') if i.get('token') else '',
                                    'name': i.get('name'),
                                    'user_id': i.get('user_id') if i.get('user_id') else '',
                                    'session_id': i.get('id')
                                }
                                dict_for_count.append(data_dict_items)

                            dict_for_deleted.append(i.get('id'))
            except (requests.ConnectionError, requests.Timeout, requests.RequestException):
                continue

        data = unique_and_count(dict_for_count)

        grouped = defaultdict(lambda: defaultdict(list))
        for item in data:
            token = item.get("token")
            if not token:
                continue
            if token == 'xdlh68u2tciqk8':
                send_message_to_tg(f'-------- Token in after if --- {base_unix_time} ---')
                send_message_to_tg(str(item))
            grouped[token][base_unix_time].append(item)
            if token == 'xdlh68u2tciqk8':
                send_message_to_tg(f"Token={token}, base_unix_time={base_unix_time}, grouped_now={list(grouped[token].keys())}")

        for token, time_dict in grouped.items():
            if token == 'xdlh68u2tciqk8':
                send_message_to_tg(f"IN GROUPED: token={token}, keys={list(time_dict.keys())}")
                send_message_to_tg('=========== Token in grouped ===========')
            existing = cache.get(token, {})
            cleaned = {
                ts: items
                for ts, items in existing.items()
                if base_unix_time - int(ts) <= 172800000
            }
            cleaned.update(time_dict)

            if token == 'xdlh68u2tciqk8':
                send_message_to_tg('=========== Token in cleaned ===========')
                send_message_to_tg(str({
                    "base_unix_time": base_unix_time,
                    "incoming_time_dict": time_dict
                }))

            cache.set(token, cleaned)

        # serializer = SessionSerializer(data=data, many=True)
        # if not serializer.is_valid():
        #     send_message_to_tg(serializer.errors)
        #     return Response(serializer.errors)
        # serializer.save()

        no_deleted = list(StatusSessionModel.objects.filter(deleted_at=1).values_list('session_id', flat=True))

        res_for_deleted_at = list(set(no_deleted) - set(dict_for_deleted))

        StatusSessionModel.objects.filter(session_id__in=res_for_deleted_at).update(deleted_at=base_unix_time)

        # session = SessionModel.objects.filter(time__lt=date_for_del)
        # session.delete()

        return Response(status=status.HTTP_200_OK)
