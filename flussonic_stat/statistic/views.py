from django.db.models import Sum
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from notify_session.models import StatusSessionModel
from statistic.models import SessionModel
from statistic.serializers import SessionSerializer

import requests
from itertools import groupby
import datetime


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

            list_ip = ['50.7.89.234', '162.19.136.10', '141.95.65.149', '145.239.140.7', '185.132.132.212']
            dict_for_count = []
            dict_for_deleted = []

            for ip in list_ip:
                res = requests.get(f'http://admin:qwertystream@{ip}:89/flussonic/api/sessions').json()

                if res.get('sessions', False):

                    for i in res.get('sessions'):
                        data_dict_sessions = {
                            'source': f'{ip}',
                            'ip': i.get('ip'),
                            'token': i.get('token') if i.get('token') else '',
                            'name': i.get('name'),
                            'user_id': i.get('user_id') if i.get('user_id') else '',
                            'session_id': i.get('session_id')
                        }

                        dict_for_count.append(data_dict_sessions)
                        dict_for_deleted.append(i['session_id'])

                elif res.get('items', False):

                    for i in res.get('items'):
                        if i.get('type') == 'play':
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
                return Response(serializer.errors)
            serializer.save()

            no_deleted = list(StatusSessionModel.objects.filter(deleted_at=1).values_list('session_id', flat=True))

            res_for_deleted_at = list(set(no_deleted) - set(dict_for_deleted))

            StatusSessionModel.objects.filter(session_id__in=res_for_deleted_at).update(deleted_at=base_unix_time)

            session = SessionModel.objects.filter(time__lt=date_for_del)
            session.delete()

            return Response(serializer.data)

        except TimeoutError:
            print('Timeout')


class StatForUserConnectionsView(APIView):

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        msg = {'status': token}
        return Response(msg, status.HTTP_200_OK)
