from django.db import models
from django.core.cache import cache

ALLOWED_IPS_CACHE_KEY = "allowed_server_ips"
ALLOWED_IPS_TTL = 86400

class ProviderModel(models.Model):
    class Meta:
        db_table = 'provider'
        verbose_name = 'Провайдер'
        verbose_name_plural = 'Провайдеры'

    name = models.CharField(unique=True, max_length=255)
    id_tg = models.IntegerField(unique=True)

    def __str__(self):
        return f'{self.name}'


class SourceModel(models.Model):
    class Meta:
        db_table = 'source'
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'

    provider = models.ForeignKey(ProviderModel, on_delete=models.CASCADE)
    url = models.CharField(unique=True, max_length=255)


class ServerModel(models.Model):
    class Meta:
        db_table = 'server'
        verbose_name = 'Сервер'
        verbose_name_plural = 'Сервера'

    dyndns = models.CharField(unique=True, max_length=255)
    url = models.CharField(unique=False, max_length=255, blank=True)
    ip = models.GenericIPAddressField()

    def __str__(self):
        return f"{self.dyndns} ({self.ip})"

    def save(self, *args, **kwargs):
        cache.delete(ALLOWED_IPS_CACHE_KEY)
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        cache.delete(ALLOWED_IPS_CACHE_KEY)
        super().delete(*args, **kwargs)
