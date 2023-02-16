import requests

from datetime import datetime
from django.db.models import Count
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from monitoring.models import ChannelAstraModel, OnAirStatusModel
from monitoring.serializers import OnAirStatusSerializer
from utils.get_client_ip import get_client_ip

from django.conf import settings


class AstraMonitoringView(APIView):

    def get(self, request):
        url = f'https://api.telegram.org/{settings.TOKEN_TG}/sendMessage'
        chat_id = settings.CHAT_ID_TG
        timestamp_now = int(datetime.utcnow().timestamp())
        qs_for_tg = OnAirStatusModel.objects.filter(timestamp__gt=timestamp_now - 60)
        if qs_for_tg.exists():
            res = qs_for_tg.values('channel_id__name_channel', 'channel_id__ip_server').annotate(
                count=Count('channel_id__name_channel'))
            text = "\n".join(
                [item['channel_id__ip_server'] + ' - ' + item[
                    'channel_id__name_channel'] + ' - ' + 'потеряных пакетов' + ' - ' + str(item['count']) for item in
                 res])
            requests.post(url, data={'chat_id': chat_id, 'text': text})

        OnAirStatusModel.objects.filter(timestamp__lt=timestamp_now - 86400).delete()
        return Response(status.HTTP_200_OK)

    def post(self, request):
        all_keys = set().union(*(d.keys() for d in request.data))
        ip = get_client_ip(request)
        if 'channel' in all_keys:
            response = requests.get(f'http://{ip}:321/playlist.m3u8')
            res = response.text.splitlines()
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
        else:
            keys = ['onair', 'timestamp', 'channel_id']
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

        return Response(status.HTTP_200_OK)
