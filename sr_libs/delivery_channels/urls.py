from django.urls import path
from .views import UserEventStreamView

urlpatterns = [
    path("events/", UserEventStreamView.as_view(), name="live-events"),
]
