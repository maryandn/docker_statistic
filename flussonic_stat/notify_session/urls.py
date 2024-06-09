from django.urls import path
from . import views
from .views import StatusSessionsView, OpenedClosedSessionsView, OpenedSessionsForBillingView, \
    StatForUserConnectionsView, StatusPlayClosedView, StatusPlayStartedView, StatForUserConnectionsIpView, \
    StatForUserConnectionsSessionView, ClearAllSessionsView

urlpatterns = [
    path('', StatusSessionsView.as_view()),
    path('play_started', StatusPlayStartedView.as_view()),
    path('play_closed', StatusPlayClosedView.as_view()),
    path('rq/', views.notify),
    path('forrechart/<str:pk>', OpenedClosedSessionsView.as_view()),
    path('forbilling/<str:pk>', OpenedSessionsForBillingView.as_view()),
    path('access/<str:token>', StatForUserConnectionsView.as_view()),
    path('access/ip/<str:token>', StatForUserConnectionsIpView.as_view()),
    path('access/sessions/<str:token>', StatForUserConnectionsSessionView.as_view()),
    path('clear/all_sessions', ClearAllSessionsView.as_view()),
]
