from django.urls import path, re_path
from statistic.views import TokenStatView, GetStatView, LastSessionsView, ListSessionsView

urlpatterns = [
    path('getstat', GetStatView.as_view()),
    path('<str:pk>', TokenStatView.as_view()),
    path('last/<str:pk>', LastSessionsView.as_view()),
    path('list/<str:pk>', ListSessionsView.as_view()),
]
