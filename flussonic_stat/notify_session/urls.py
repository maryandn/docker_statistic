from django.urls import path
from . import views
from .views import StatusSessionsView, OpenedClosedSessionsView, OpenedSessionsForBillingView

urlpatterns = [
    path('', StatusSessionsView.as_view()),
    path('rq/', views.notify),
    path('forrechart/<str:pk>', OpenedClosedSessionsView.as_view()),
    path('forbilling/<str:pk>', OpenedSessionsForBillingView.as_view()),
]
