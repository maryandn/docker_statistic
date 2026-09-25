from django.urls import path
from statistic.views import GetStatView, TokenCacheStatView, AllSessionsUserView, TokenSessionsUserView, \
    OverLimitTokensView

urlpatterns = [
    path('getstat', GetStatView.as_view()),
    path('count/allsession', AllSessionsUserView.as_view()),
    path('count/tokensession/<str:pk>', TokenSessionsUserView.as_view()),
    path('count/overlimit/', OverLimitTokensView.as_view()),
    path('<str:pk>', TokenCacheStatView.as_view()),
]
