from django.db import models


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
    ip = models.GenericIPAddressField()
