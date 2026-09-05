from django.db import models


class ChannelListModel(models.Model):
    class Meta:
        db_table = 'notify_channel'
        verbose_name = 'Канал'
        verbose_name_plural = 'Каналы'

    name_channel = models.CharField(unique=True, max_length=10)
    title_channel = models.CharField(max_length=60)

    def __str__(self):
        return f"{self.name_channel}  {self.title_channel}"
