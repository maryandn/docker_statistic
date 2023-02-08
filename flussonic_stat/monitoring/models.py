from django.db import models


class ChannelAstraModel(models.Model):
    class Meta:
        db_table = 'astra_channel'
        verbose_name = 'Астра канал'
        verbose_name_plural = 'Астра каналы'

    name_channel = models.CharField(unique=True, max_length=255)
    id_astra = models.CharField(unique=True, max_length=4)
    ip_server = models.GenericIPAddressField()


class OnAirStatusModel(models.Model):
    class Meta:
        db_table = 'onair_status'
        verbose_name = 'Статус канала'
        verbose_name_plural = 'Статус каналов'

    timestamp = models.BigIntegerField()
    channel_id = models.ForeignKey(ChannelAstraModel, on_delete=models.CASCADE)
    onair = models.BooleanField()
