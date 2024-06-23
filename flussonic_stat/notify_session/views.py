import json

import requests
import time

from django.db.models import Count
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from drf_multiple_model.views import ObjectMultipleModelAPIView
from rest_framework import status
from rest_framework.generics import ListAPIView

from rest_framework.views import APIView
from rest_framework.response import Response

from config.models import ServerModel
from notify_session.models import StatusSessionModel
from notify_session.serializers import SessionOpenedSerializer, SessionClosedSerializer, \
    OpenedSessionsForBillingSerializer
from utils.get_client_ip import get_client_ip


def transform_data(data):
    sessions_by_ip = {}

    for session in data:
        ip = session["ip"]
        media = session["my_field"]
        session_id = session["session_id"]
        created_at = session['created_at']

        if ip in sessions_by_ip:
            sessions_by_ip[ip]["count"] += 1
            sessions_by_ip[ip]["sessions"].append({"media": media, 'created_at': created_at, "session_id": session_id})
        else:
            sessions_by_ip[ip] = {"ip": ip, "count": 1,
                                  "sessions": [{"media": media, 'created_at': created_at, "session_id": session_id}]}

    return list(sessions_by_ip.values())


@csrf_exempt
def notify(request):
    ip = get_client_ip(request)
    print(json.loads(request.body))
    return HttpResponse('')


class StatusPlayStartedView(APIView):
    serializer_class = SessionOpenedSerializer

    def post(self, request):

        ip = get_client_ip(request)
        qs_server_ip_access = ServerModel.objects.filter(ip=ip)
        if not qs_server_ip_access.exists():
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        data_list = request.data

        for data in data_list:
            if data['event'] == 'play_started':
                data_to_save = {
                    'bytes_sent': data.get('bytes'),
                    'country': data.get('country'),
                    'created_at': data.get('opened_at'),
                    'deleted_at': 1,
                    'ip': data.get('ip'),
                    'last_access_time': data.get('opened_at'),
                    'media': data.get('media'),
                    'session_id': data.get('id'),
                    'token': data.get('token'),
                    'type': 'mpegts' if data.get('proto') == 'tshttp' else data.get('proto'),
                    'user_agent': data.get('user_agent'),
                    'user_id': data.get('user_id')
                }

                serializer = SessionOpenedSerializer(data=data_to_save)
                if not serializer.is_valid():
                    return Response(serializer.errors)
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class StatusPlayClosedView(APIView):

    def post(self, request):

        ip = get_client_ip(request)
        qs_server_ip_access = ServerModel.objects.filter(ip=ip)
        if not qs_server_ip_access.exists():
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        data_list = request.data

        for data in data_list:
            if data['event'] == 'play_closed':
                session_id = data['id']
                if data['token'].find('?utc=') > 0:
                    data['token'] = data['token'].split('?utc=')[0]
                StatusSessionModel.objects.filter(session_id=session_id).update(bytes_sent=data['bytes'],
                                                                                deleted_at=data['closed_at'])

                last_sessions = StatusSessionModel.objects.filter(token=data['token']).exclude(deleted_at=1)

                if len(last_sessions) > 10:
                    list_for_clear = list(last_sessions.values_list('id', flat=True))[:-10]
                    del_session_for_user = StatusSessionModel.objects.filter(id__in=list_for_clear)
                    del_session_for_user.delete()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)


class StatusSessionsView(APIView):
    serializer_class = SessionOpenedSerializer, SessionClosedSerializer

    def post(self, request):

        ip = get_client_ip(request)
        qs_server_ip_access = ServerModel.objects.filter(ip=ip)
        if not qs_server_ip_access.exists():
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        data_list = request.data

        for data in data_list:
            if data['event'] == 'session_opened':
                user_id = data.get('user_id')
                media = data.get('media')
                session_id = data.get('session_id')
                res = requests.get(
                    f'http://{settings.FLUSSONIC_LOGIN}:{settings.FLUSSONIC_PASSWORD}@{ip}:89/flussonic/api/sessions?user_id={user_id}&name={media}')
                obj = next(item for item in res.json()['sessions'] if item["session_id"] == session_id)

                data_to_save = {
                    'bytes_sent': data.get('bytes_sent'),
                    'country': data.get('country'),
                    'created_at': data.get('created_at'),
                    'deleted_at': 1,
                    'ip': obj.get('ip'),
                    'last_access_time': data.get('created_at'),
                    'media': media,
                    'session_id': session_id,
                    'token': data.get('token'),
                    'type': data.get('type'),
                    'user_agent': data.get('user_agent'),
                    'user_id': user_id
                }
                serializer = SessionOpenedSerializer(data=data_to_save)
                if not serializer.is_valid():
                    return Response(serializer.errors)
                serializer.save()

            elif data['event'] == 'session_closed':
                session_id = data['session_id']
                if data['token'].find('?utc=') > 0:
                    data['token'] = data['token'].split('?utc=')[0]
                StatusSessionModel.objects.filter(session_id=session_id).update(bytes_sent=data['bytes_sent'],
                                                                                deleted_at=data['deleted_at'])

                last_sessions = StatusSessionModel.objects.filter(token=data['token']).exclude(deleted_at=1)

                if len(last_sessions) > 10:
                    list_for_clear = list(last_sessions.values_list('id', flat=True))[:-10]
                    del_session_for_user = StatusSessionModel.objects.filter(id__in=list_for_clear)
                    del_session_for_user.delete()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK)


class OpenedClosedSessionsView(ObjectMultipleModelAPIView):

    def get_querylist(self):
        token = self.kwargs.get('pk')

        querylist = (
            {
                'queryset': StatusSessionModel.objects.filter(token=token, deleted_at=1).order_by('-created_at'),
                'serializer_class': SessionOpenedSerializer,
                'label': 'opened'
            },
            {
                'queryset': StatusSessionModel.objects.filter(token=token, deleted_at__gt=2).order_by('-deleted_at'),
                'serializer_class': SessionOpenedSerializer,
                'label': 'closed'
            },
            {
                'queryset': StatusSessionModel.objects.filter(token=token)[0:1],
                'serializer_class': SessionOpenedSerializer,
                'label': 'user_id'
            }
        )
        return querylist


class OpenedSessionsForBillingView(ListAPIView):
    serializer_class = OpenedSessionsForBillingSerializer
    model = StatusSessionModel

    def get_queryset(self):
        token = self.kwargs.get('pk')
        qs = self.model.objects.filter(token=token, deleted_at=1)
        return qs


class StatForUserConnectionsView(APIView):

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        qs = StatusSessionModel.objects.filter(token=token, deleted_at=1,
                                               created_at__lt=round(time.time() * 1000) - 45000).order_by('-created_at')

        return Response(
            {
                'all_count': qs.count(),
                'data': transform_data(SessionOpenedSerializer(qs, many=True).data)
            }, status.HTTP_200_OK)


class StatForUserConnectionsIpView(APIView):

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        qs = StatusSessionModel.objects.filter(token=token, deleted_at=1,
                                               created_at__lt=round(time.time() * 1000) - 45000).values('ip').distinct()
        return Response(qs, status.HTTP_200_OK)


class StatForUserConnectionsSessionView(APIView):

    def get(self, request, *args, **kwargs):
        token = kwargs.get('token')
        qs = StatusSessionModel.objects.filter(token=token, deleted_at=1,
                                               created_at__lt=round(time.time() * 1000) - 45000).aggregate(
            all_count=Count('id'))
        return Response(qs, status.HTTP_200_OK)
