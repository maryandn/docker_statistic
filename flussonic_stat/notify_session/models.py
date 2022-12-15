from django.db import models


class StatusSessionModel(models.Model):
    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'
        db_table = 'notify_session'
        ordering = ['created_at']

    bytes_sent = models.BigIntegerField(blank=True)
    country = models.CharField(max_length=4, blank=True)
    created_at = models.BigIntegerField()
    deleted_at = models.BigIntegerField(blank=True)
    ip = models.GenericIPAddressField()
    last_access_time = models.BigIntegerField()
    media = models.CharField(max_length=10)
    session_id = models.CharField(max_length=55)
    token = models.CharField(max_length=50)
    type = models.CharField(max_length=10)
    user_agent = models.CharField(max_length=255)
    user_id = models.CharField(max_length=255)
