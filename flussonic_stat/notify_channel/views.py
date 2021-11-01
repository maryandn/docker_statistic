from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
import json
import requests

from notify_channel.models import ChannelListModel
from notify_channel.serializers import ChannelListSerializer
from utils.get_client_ip import get_client_ip


@csrf_exempt
def notify(request):
    print(json.loads(request.body)[0])
    return HttpResponse('')


class ChannelListView(APIView):
    serializer_class = ChannelListSerializer

    def post(self, request):

        data = request.data[0]
        ip = get_client_ip(request)

        try:
            if data['event'] == 'config_reloaded':
                res = requests.get(f'http://admin:qwertystream@{ip}:89/flussonic/api/streams').json()
                list_channels = res.get('streams')
                list = []
                for item in list_channels:
                    dict = {'name_channel': item.get('name'), 'title_channel': item.get('title')}
                    list.append(dict)

                for channel in list:
                    name_channel = channel.pop('name_channel')
                    obj = ChannelListModel.objects.update_or_create(name_channel=name_channel,
                                                                    defaults=channel)

            else:
                print('other_event')
            return Response(status.HTTP_200_OK)
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
