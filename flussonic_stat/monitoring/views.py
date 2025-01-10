import requests

from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse

from config.models import ServerModel
from monitoring.models import ChannelAstraModel, OnAirStatusModel
from monitoring.serializers import OnAirStatusSerializer
from utils.get_client_ip import get_client_ip
from utils.tg_send_message import send_message_to_tg


class AstraMonitoringView(APIView):

    def get(self, request):
        timestamp_now = int(datetime.utcnow().timestamp())
        qs_for_tg = OnAirStatusModel.objects.filter(timestamp__gt=timestamp_now - 61)
        if qs_for_tg.exists():
            res = qs_for_tg.values('channel_id__name_channel', 'channel_id__ip_server', 'count')
            text = "\n".join(
                [item['channel_id__ip_server'] + ' - ' + item[
                    'channel_id__name_channel'] + ' - ' + 'потеряных пакетов' + ' - ' + str(item['count']) for item in
                 res])
            send_message_to_tg(text)

        OnAirStatusModel.objects.filter(timestamp__lt=timestamp_now - 86400).delete()
        return Response(status=status.HTTP_200_OK)

    def post(self, request):

        ip = get_client_ip(request)
        send_message_to_tg(ip)
        qs_server_ip_access = ServerModel.objects.filter(ip=ip)
        if not qs_server_ip_access.exists():
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

        all_keys = set().union(*(d.keys() for d in request.data))

        if 'channel' in all_keys:
            send_message_to_tg(all_keys)
            response = requests.get(f'http://{ip}:320/playlist.m3u8')
            res = response.text.splitlines()
            send_message_to_tg(res)
            res.pop(0)
            res = ''.join(res)[1:].split('#')
            list_id_astra = []
            for item in res:
                item_separator = item.find('http')
                name_channel = item[10:item_separator]
                id_channel = item[-15:-11]
                list_id_astra.append(id_channel)
                data_item = {
                    'name_channel': name_channel,
                    'id_astra': id_channel,
                    'ip_server': ip
                }

                ChannelAstraModel.objects.get_or_create(id_astra=id_channel, ip_server=ip, defaults=data_item)
            qs = ChannelAstraModel.objects.exclude(id_astra__in=list_id_astra).filter(ip_server=ip)
            qs.delete()
        elif 'dvb_id' in all_keys:
            print('++dvb++', all_keys)
        elif 'onair' in all_keys:
            send_message_to_tg('onair')
            keys = ['onair', 'timestamp', 'channel_id', 'count']
            data_keys = [{k: item[k] for k in keys} for item in request.data if item['onair'] == False]
            if data_keys:
                get_channel_from_request = list(set([i['channel_id'] for i in data_keys]))
                qs = ChannelAstraModel.objects.filter(id_astra__in=get_channel_from_request, ip_server=ip)
                if qs.exists():
                    for data_key in data_keys:
                        data_key["channel_id"] = qs.values()[0]['id']

            serializer = OnAirStatusSerializer(data=data_keys, many=True)
            if not serializer.is_valid():
                return Response(serializer.errors)
            serializer.save()
        else:
            text = f'{ip} Incorrect request'
            send_message_to_tg(text)

        return Response(status=status.HTTP_200_OK)
