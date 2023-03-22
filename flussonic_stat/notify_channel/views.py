import json
import requests

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from config.models import ServerModel, SourceModel
from notify_channel.models import ChannelListModel
from notify_channel.serializers import ChannelListSerializer
from utils.get_client_ip import get_client_ip
from utils.tg_send_message import send_message_to_tg


def request_flussonic(ip):
    res = requests.get(
        f'http://{settings.FLUSSONIC_LOGIN}:{settings.FLUSSONIC_PASSWORD}@{ip}:89/flussonic/api/streams').json()
    return res


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
                res = request_flussonic('50.7.89.234')
                list_channels = res.get('streams')
                list_of_dict = []
                for item in list_channels:
                    dict_channel = {'name_channel': item.get('name'), 'title_channel': item.get('title')}
                    list_of_dict.append(dict_channel)
                for channel in list_of_dict:
                    name_channel = channel.pop('name_channel')
                    ChannelListModel.objects.update_or_create(name_channel=name_channel, defaults=channel)

                # count sources
                list_server = ServerModel.objects.all().values('ip')
                list_sources = [x.get('url') for x in SourceModel.objects.all().values('url')]
                list_urls = []
                list_text = ['Service messages from stat:']

                for server in list_server:
                    res_all = request_flussonic(server.get('ip'))
                    for item in res_all.get('streams'):
                        list_urls.append(str(list(item.get('urls').keys())[0]))

                for item_count in list_sources:
                    count = sum(1 for s in list_urls if f'{item_count}' in s)
                    list_text.append(' ' + str(f"{item_count}: {count}"))
                text = '\n'.join(list_text)
                send_message_to_tg(text)

            else:
                print('other_event')
            return Response(status.HTTP_200_OK)
        except:
            return Response(status.HTTP_400_BAD_REQUEST)
