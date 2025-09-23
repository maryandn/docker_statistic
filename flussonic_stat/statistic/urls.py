from django.urls import path
from statistic.views import GetStatView, TokenMysqlStatView, TokenCacheStatView

urlpatterns = [
    path('getstat', GetStatView.as_view()),
    path('<str:pk>', TokenCacheStatView.as_view()),
]
