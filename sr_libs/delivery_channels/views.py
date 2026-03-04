from django_eventstream.viewsets import EventsViewSet
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class MyEventsViewSet(EventsViewSet):
    permission_classes = [AllowAny]

    def get_channels(self, request=None, *args, **kwargs):
        if not request:
            print("No request")
            return []

        user = getattr(request, "user", None)

        if not user or not user.is_authenticated:
            token = request.GET.get("token")
            if token:
                try:
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(token)
                    user = jwt_auth.get_user(validated_token)
                    request.user = user
                    print("Authenticated user:", user.id)
                except Exception as e:
                    print("JWT failed:", e)
                    user = AnonymousUser()
            else:
                print("No token")
                user = AnonymousUser()

        if not user.is_authenticated:
            print("Returning empty channels")
            return []

        channel = f"user-{user.id}"
        print("Subscribing to channel:", channel)
        return [channel]
