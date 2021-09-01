from django.db import models
import datetime


class SessionModel(models.Model):
    class Meta:
        db_table = 'statistic'

    time = models.BigIntegerField()
    name = models.CharField(max_length=16)
    source = models.GenericIPAddressField()
    ip = models.GenericIPAddressField()
    token = models.CharField(max_length=255, blank=True)
    user_id = models.CharField(max_length=255, blank=True)
    count = models.IntegerField(blank=True)

    def save(self, *args, **kwargs):
        self.time = int(datetime.datetime.now().strftime('%s')) // 60 * 60 * 1000
        return super(SessionModel, self).save(*args, **kwargs)
