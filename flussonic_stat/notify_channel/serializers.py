from rest_framework import serializers

from notify_channel.models import ChannelListModel


class ChannelListSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelListModel
        fields = ['name_channel', 'title_channel']
