from django.urls import path

from .views import AstraMonitoringView

urlpatterns = [
    path('', AstraMonitoringView.as_view()),
]
