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


def request_flussonic(ip, url):
    res = requests.get(
        f'http://{settings.FLUSSONIC_LOGIN}:{settings.FLUSSONIC_PASSWORD}@{ip}:89/{url}/streams').json()
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
        qs_server_ip_access = ServerModel.objects.filter(ip=ip)

        if not qs_server_ip_access.exists():
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        url = qs_server_ip_access.values()[0]['url']

        try:
            if data['event'] == 'config_reloaded':
                res = request_flussonic(ip, url)
                list_channels = res.get('streams', [])

                for channel in list_channels:
                    name = channel.get('name', '')
                    title = channel.get('title', '')

                    if len(name) > 6:
                        continue

                    ChannelListModel.objects.update_or_create(name_channel=name, defaults={'title_channel': title})

                # count sources
                list_server = ServerModel.objects.all().values('ip', 'url')
                list_sources = [x.get('url') for x in SourceModel.objects.all().values('url')]
                list_urls = []
                list_text = ['Service messages from stat:']
                for server in list_server:
                    res_all = request_flussonic(server.get('ip'), server.get('url'))
                    for item in res_all.get('streams'):
                        if item.get('urls'):
                            list_urls.append(str(list(item.get('urls').keys())[0]))

                for item_count in list_sources:
                    count = sum(1 for s in list_urls if f'{item_count}' in s)
                    list_text.append(' ' + str(f"{item_count}: {count}"))
                text = '\n'.join(list_text)

                send_message_to_tg(text)

            else:
                print('other_event')
            return Response(status=status.HTTP_200_OK)
        except Exception as e:
            error_text = f"Помилка: {type(e).__name__} - {str(e)}"
            send_message_to_tg(error_text)
            return Response(status=status.HTTP_400_BAD_REQUEST)
