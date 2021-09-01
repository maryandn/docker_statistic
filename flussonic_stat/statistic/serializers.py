from rest_framework import serializers

from statistic.models import SessionModel


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionModel
        fields = ('time', 'source', 'name', 'token', 'user_id', 'ip', 'count',)
        read_only_fields = ('time',)
