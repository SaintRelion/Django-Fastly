from django_eventstream.viewsets import configure_events_view_set
from django.contrib.auth.models import AnonymousUser
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.authentication import JWTAuthentication


def get_user_from_request(request):
    token = request.GET.get("token")
    if not token:
        return AnonymousUser()

    try:
        user_authenticator = JWTAuthentication()
        validated_token = user_authenticator.get_validated_token(token)
        user = user_authenticator.get_user(validated_token)
        return user
    except Exception:
        return AnonymousUser()


router = DefaultRouter()
router.register(
    "events",
    configure_events_view_set(
        channels=lambda request: (
            [f"user-{get_user_from_request(request).id}"]
            if request.user.is_authenticated
            else []
        )
    ),
    basename="user-events",
)

urlpatterns = router.urls
