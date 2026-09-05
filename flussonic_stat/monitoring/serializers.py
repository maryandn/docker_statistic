from rest_framework import serializers

from monitoring.models import ChannelAstraModel, OnAirStatusModel


class ChannelAstraSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChannelAstraModel
        fields = '__all__'


class OnAirStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnAirStatusModel
        fields = '__all__'
