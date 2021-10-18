from rest_framework import serializers

from notify_session.models import StatusSessionModel


class SessionOpenedSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatusSessionModel
        fields = '__all__'

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
