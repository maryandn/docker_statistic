from django.contrib import admin

from notify_channel.models import ChannelListModel


@admin.register(ChannelListModel)
class ChannelListAdmin(admin.ModelAdmin):
    list_display = ('name_channel', 'title_channel',)
    search_fields = ['name_channel']
