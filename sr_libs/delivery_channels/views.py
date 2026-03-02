from rest_framework.routers import DefaultRouter
from .views import configure_events_view_set

router = DefaultRouter()
router.register(
    "events",
    configure_events_view_set(
        channels=lambda request: [f"user-{request.user.id}"],
        message_types=["message", "info"],
    ),
    basename="user-events",
)

urlpatterns = router.urls
