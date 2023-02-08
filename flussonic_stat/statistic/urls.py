from django.urls import path
from statistic.views import TokenStatView, GetStatView, StatForUserConnectionsView

urlpatterns = [
    path('getstat', GetStatView.as_view()),
    path('<str:pk>', TokenStatView.as_view()),
    path('access/<str:token>', StatForUserConnectionsView.as_view()),
]
