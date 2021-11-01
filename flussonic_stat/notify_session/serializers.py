from rest_framework import serializers

from notify_channel.models import ChannelListModel
from notify_channel.serializers import ChannelListSerializer
from notify_session.models import StatusSessionModel


class SessionOpenedSerializer(serializers.ModelSerializer):
    my_field = serializers.SerializerMethodField()

    class Meta:
        model = StatusSessionModel
        fields = [
            'id',
            'bytes_sent',
            'country',
            'created_at',
            'deleted_at',
            'ip',
            'last_access_time',
            'media',
            'session_id',
            'token',
            'type',
            'user_agent',
            'user_id',
            'my_field'
        ]
        read_only_fields = ('my_field',)

    def get_my_field(self, obj):
        qs = ChannelListModel.objects.filter(name_channel=obj.media).first()
        return ChannelListSerializer(qs).data

    def validate_token(self, value):
        if value.find('?utc=') > 0:
            value = value.split('?utc=')[0]
        return value


class SessionClosedSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusSessionModel
        fields = ('deleted_at',)


class OpenedSessionsForBillingSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusSessionModel
        fields = ('media', 'ip')
