from django.db.models import Sum
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework import status, generics
from rest_framework.response import Response
from statistic.models import SessionModel
from statistic.serializers import SessionSerializer

import requests
from itertools import groupby
import datetime
import json


def canonicalize_dict(x):
    return sorted(x.items(), key=lambda x: hash(x[0]))


def unique_and_count(lst):
    grouper = groupby(sorted(map(canonicalize_dict, lst)))
    return [dict(k + [("count", len(list(g)))]) for k, g in grouper]


@csrf_exempt
def notify(request):
    print(json.loads(request.body))
    return HttpResponse('')


class TokenStatView(generics.ListAPIView):
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):

        base_unix_time = int(datetime.datetime.now().strftime('%s')) // 60 * 60 * 1000
        date_list = [base_unix_time - x * 60000 for x in range(24 * 60)]

        token_or_ip = kwargs.get('pk')

        if token_or_ip.count('.') == 3 and all(0 <= int(num) < 256 for num in token_or_ip.rstrip().split('.')):
            result = SessionModel.objects.filter(ip=token_or_ip, time__in=date_list).values_list('time').annotate(
                count=Sum('count')).order_by('time')

            diff = list(set(date_list) - set([i[0] for i in list(result)]))

            result = list(result)

            for i in diff:
                result.append((i, 0))

            result.sort(key=lambda tup: tup[0])

        else:
            result = SessionModel.objects.filter(token=token_or_ip, time__in=date_list).values_list('time').annotate(
                count=Sum('count')).order_by('time')

            diff = list(set(date_list) - set([i[0] for i in list(result)]))

            result = list(result)

            for i in diff:
                result.append((i, 0))

            result.sort(key=lambda tup: tup[0])

        return Response(result, status.HTTP_200_OK)


class LastSessionsView(generics.ListAPIView):
    serializer_class = SessionSerializer

    def get(self, request, *args, **kwargs):
        base_unix_time = int(datetime.datetime.now().strftime('%s')) // 60 * 60 * 1000

        token_or_ip = kwargs.get('pk')

        if token_or_ip.count('.') == 3 and all(0 <= int(num) < 256 for num in token_or_ip.rstrip().split('.')):
            result = SessionModel.objects.filter(ip=token_or_ip, time=base_unix_time).values('time', 'ip').annotate(
                count=Sum('count')).order_by('time')

        else:
            result = SessionModel.objects.filter(token=token_or_ip, time=base_unix_time).values('time', 'ip').annotate(
                count=Sum('count')).order_by('time')

        return Response(result, status.HTTP_200_OK)


class ListSessionsView(APIView):
    serializer_class = SessionSerializer

    def get(self, request, *args, **kwargs):

        token_or_ip = kwargs.get('pk')

        if token_or_ip.count('.') == 3 and all(0 <= int(num) < 256 for num in token_or_ip.rstrip().split('.')):
            result = SessionModel.objects.filter(ip=token_or_ip).values('time', 'name').order_by('-time')
        else:
            result = SessionModel.objects.filter(token=token_or_ip).values('time', 'name').order_by('-time')

        return Response(result, status.HTTP_200_OK)


class GetStatView(APIView):
    serializer_class = SessionSerializer
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        try:
            list_ip = ['50.7.136.26', '51.195.4.225', '51.195.7.141', '145.239.140.7']
            dict_for_count = []

            for ip in list_ip:
                res = requests.get(f'http://admin:qwertystream@{ip}:89/flussonic/api/sessions').json()

                for i in res['sessions']:
                    i.setdefault('source', f'{ip}')
                    i.setdefault('token', '')
                    i.setdefault('user_agent', '')
                    i.setdefault('referer', '')
                    i.setdefault('current_time', '')
                    i.setdefault('user_id', '')
                    del i['duration'], i['session_id'], i['country'], i['id'], i['bytes_sent'], i['created_at'], i[
                        'user_agent'], i[
                        'referer'], i['type'], i['current_time']
                    if i.get('token').find('=') > 0:
                        i.update({'token': i.get('token').partition('?utc=')[0]})

                    if i.get('user_id').find(':') > 0:
                        i.update({'user_id': i.get('user_id').partition(':')[2]})
                    dict_for_count.append(i)

            data = unique_and_count(dict_for_count)
            serializer = SessionSerializer(data=data, many=True)
            if not serializer.is_valid():
                return Response(serializer.errors)
            serializer.save()

            return Response(serializer.data)

        except TimeoutError:
            print('Timeout')
