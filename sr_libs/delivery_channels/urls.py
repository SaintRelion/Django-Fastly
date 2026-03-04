from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django_eventstream.viewsets import EventsViewSet

router = DefaultRouter()

router.register("events", EventsViewSet, basename="events")  # no fixed channels

urlpatterns = router.urls
