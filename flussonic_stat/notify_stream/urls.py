from django.urls import path
from .views import StatusStreamView

urlpatterns = [
    path('', StatusStreamView.as_view()),
]
