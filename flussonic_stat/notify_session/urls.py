from django.urls import path
from .views import OpenedClosedSessionsView, OpenedSessionsForBillingView, StatusPlayClosedView, StatusPlayStartedView

urlpatterns = [
    path('play_started', StatusPlayStartedView.as_view()),
    path('play_closed', StatusPlayClosedView.as_view()),
    path('forrechart/<str:pk>', OpenedClosedSessionsView.as_view()),
    path('forbilling/<str:pk>', OpenedSessionsForBillingView.as_view()),
]
