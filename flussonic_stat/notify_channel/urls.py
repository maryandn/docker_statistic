from django.urls import path
from . import views
from .views import ChannelListView

urlpatterns = [
    path('', ChannelListView.as_view()),
    path('rq/', views.notify),
]
