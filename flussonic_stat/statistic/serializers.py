from rest_framework import serializers

from statistic.models import SessionModel


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionModel
        fields = ('time', 'source', 'name', 'session_id', 'token', 'user_id', 'ip', 'count',)
        read_only_fields = ('time',)

    def validate_token(self, value):
        if value.find('?utc=') > 0:
            value = value.split('?utc=')[0]
        return value

    def validate_user_id(self, value):
        if value.find(':') > 0:
            value = value.split(':')[1]
        return value
