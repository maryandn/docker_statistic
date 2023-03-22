from django.contrib import admin

from statistic.models import SessionModel


@admin.register(SessionModel)
class ChannelListAdmin(admin.ModelAdmin):
    list_display = ('name', 'session_id', 'source', 'ip', 'token', 'user_id', 'count')
    search_fields = ['token']
    ordering = ['time']
