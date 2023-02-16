from django.urls import path
from statistic.views import TokenStatView, GetStatView

urlpatterns = [
    path('getstat', GetStatView.as_view()),
    path('<str:pk>', TokenStatView.as_view()),
]
