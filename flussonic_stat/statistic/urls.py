from django.urls import path
from statistic.views import GetStatView, TokenCacheStatView, AllSessionsUserView

urlpatterns = [
    path('getstat', GetStatView.as_view()),
    path('allsessions', AllSessionsUserView.as_view()),
    path('<str:pk>', TokenCacheStatView.as_view()),
]
