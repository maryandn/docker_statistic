from django.urls import path
from .views import ChannelListView

urlpatterns = [
    path('', ChannelListView.as_view()),
]
