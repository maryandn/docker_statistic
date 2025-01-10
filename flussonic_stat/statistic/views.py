import json

from django.db.models import Sum
from django.conf import settings
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


class TokenStatView(generics.ListAPIView):
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


class GetStatView(APIView):
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            base_unix_time = int(datetime.datetime.now().strftime('%s')) // 60 * 60 * 1000
            date_for_del = base_unix_time - 172800000

            list_server = ServerModel.objects.all().values('ip', 'url')
            dict_for_count = []
            dict_for_deleted = []

            for server in list_server:
                ip = server.get('ip')
                url = server.get('url')
                res = requests.get(
                    f'http://{settings.FLUSSONIC_LOGIN}:{settings.FLUSSONIC_PASSWORD}@{ip}:89/{url}/sessions').json()

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

                            dict_for_deleted.append(i['id'])

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

                            dict_for_deleted.append(i['id'])

            data = unique_and_count(dict_for_count)

            serializer = SessionSerializer(data=data, many=True)
            if not serializer.is_valid():
                send_message_to_tg(serializer.errors)
                return Response(serializer.errors)
            serializer.save()

            no_deleted = list(StatusSessionModel.objects.filter(deleted_at=1).values_list('session_id', flat=True))

            res_for_deleted_at = list(set(no_deleted) - set(dict_for_deleted))

            StatusSessionModel.objects.filter(session_id__in=res_for_deleted_at).update(deleted_at=base_unix_time)

            session = SessionModel.objects.filter(time__lt=date_for_del)
            session.delete()

            # return Response(serializer.data)
            return Response(status=status.HTTP_200_OK)

        except TimeoutError:
            print('Timeout')
