from django.contrib import admin

from config.models import ProviderModel, SourceModel, ServerModel


@admin.register(ProviderModel)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('name', 'id_tg')
    search_fields = ['name']


@admin.register(SourceModel)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('get_provider', 'url')
    search_fields = ['get_provider']

    def get_provider(self, obj):
        return obj.provider.name


@admin.register(ServerModel)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('dyndns', 'url', 'ip')
    search_fields = ['dyndns']
