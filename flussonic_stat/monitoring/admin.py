from django.contrib import admin

from monitoring.models import ChannelAstraModel, OnAirStatusModel


@admin.register(ChannelAstraModel)
class ChannelAstraAdmin(admin.ModelAdmin):
    list_display = ('name_channel', 'id_astra', 'ip_server')
    search_fields = ['name_channel']


@admin.register(OnAirStatusModel)
class OnAirStatusAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'channel_id', 'onair')
    search_fields = ['channel_id']
