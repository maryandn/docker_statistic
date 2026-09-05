from datetime import datetime

from django.contrib import admin

from monitoring.models import ChannelAstraModel, OnAirStatusModel


@admin.register(ChannelAstraModel)
class ChannelAstraAdmin(admin.ModelAdmin):
    list_display = ('name_channel', 'id_astra', 'ip_server')
    search_fields = ['name_channel']


@admin.register(OnAirStatusModel)
class OnAirStatusAdmin(admin.ModelAdmin):
    list_display = ('get_timestamp', 'get_channel_id', 'onair')
    search_fields = ['channel_id__name_channel']

    def get_channel_id(self, obj):
        return obj.channel_id.name_channel

    def get_timestamp(self, obj):
        ts = obj.timestamp
        return datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')