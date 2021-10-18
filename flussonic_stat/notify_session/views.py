from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from drf_multiple_model.views import ObjectMultipleModelAPIView
from rest_framework import status
from rest_framework.generics import ListAPIView

from rest_framework.views import APIView
from rest_framework.response import Response
import json

from notify_session.models import StatusSessionModel
from notify_session.serializers import SessionOpenedSerializer, SessionClosedSerializer, \
    OpenedSessionsForBillingSerializer


@csrf_exempt
def notify(request):
    print(json.loads(request.body)[0])
    return HttpResponse('')


class StatusSessionsView(APIView):
    serializer_class = SessionOpenedSerializer, SessionClosedSerializer

    def post(self, request):

        data = request.data[0]
        print('----1----', request.data)

        try:
            del data['access'], data['active'], data['auth_time'], data['current_time'], data['delete_time'], data[
                'first_access_time'], data['last_verify_time'], data['loglevel'], data['max_sessions'], \
                data['event_id'], data['name'], data['query_string'], data['server'], data['soft_limitation'], data[
                'user_name'], data['utc_ms'], data['referer']

            if data['event'] == 'session_opened':
                del data['event']
                data['deleted_at'] = 1
                serializer = SessionOpenedSerializer(data=data)
                if not serializer.is_valid():
                    return Response(serializer.errors)
                serializer.save()

            elif data['event'] == 'session_closed':
                del data['event']
                session_id = data['session_id']
                if data['token'].find('?utc=') > 0:
                    data['token'] = data['token'].split('?utc=')[0]
                qs = StatusSessionModel.objects.filter(session_id=session_id).update(bytes_sent=data['bytes_sent'],
                                                                                     deleted_at=data['deleted_at'])

                last_sessions = StatusSessionModel.objects.filter(token=data['token']).exclude(deleted_at=1)

                if len(last_sessions) > 10:
                    list_for_clear = list(last_sessions.values_list('id', flat=True))[:-10]
                    del_session_for_user = StatusSessionModel.objects.filter(id__in=list_for_clear)
                    del_session_for_user.delete()

            else:
                print('other_event')
            return Response(status.HTTP_200_OK)
        except:
            return Response(status.HTTP_400_BAD_REQUEST)


class OpenedClosedSessionsView(ObjectMultipleModelAPIView):

    def get_querylist(self):
        token = self.kwargs.get('pk')

        querylist = (
            {'queryset': StatusSessionModel.objects.filter(token=token, deleted_at=1),
             'serializer_class': SessionOpenedSerializer,
             'label': 'opened'
             },
            {'queryset': StatusSessionModel.objects.filter(token=token, deleted_at__gt=2),
             'serializer_class': SessionOpenedSerializer,
             'label': 'closed'
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
