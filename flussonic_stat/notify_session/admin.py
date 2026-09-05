from django.contrib import admin

from notify_session.models import StatusSessionModel


@admin.register(StatusSessionModel)
class StatusSessionAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'token', 'media', 'type', 'ip', 'country', 'created_at', 'deleted_at', 'bytes_sent',)
    search_fields = ('token',)

    def get_name_service(self, obj):
        return obj.media.name_service
