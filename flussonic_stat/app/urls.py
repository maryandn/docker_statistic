from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('stat/', include('statistic.urls')),
    path('notify_session/', include('notify_session.urls')),
    path('notify_channel/', include('notify_channel.urls')),
    path('notify_stream/', include('notify_stream.urls')),
]

urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]
