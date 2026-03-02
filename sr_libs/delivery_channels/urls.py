from rest_framework.routers import DefaultRouter
from sr_libs.delivery_channels.views import MyEventsViewSet

router = DefaultRouter()
router.register("events_dynamic", MyEventsViewSet, basename="events_dynamic")

urlpatterns = router.urls
