from django_eventstream.viewsets import EventsViewSet
from rest_framework.permissions import AllowAny
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.authentication import JWTAuthentication


class MyEventsViewSet(EventsViewSet):
    permission_classes = [AllowAny]

    # Channels can be dynamic based on request.user
    def get_channels(self, request=None, *args, **kwargs):
        # 1️⃣ If no request, return empty
        if not request:
            return []

        # 2️⃣ If user is already authenticated, use it
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            # 3️⃣ Try to authenticate from query param
            token = request.GET.get("token")
            if token:
                try:
                    jwt_auth = JWTAuthentication()
                    validated_token = jwt_auth.get_validated_token(token)
                    user = jwt_auth.get_user(validated_token)
                    # temporarily assign to request.user for convenience
                    request.user = user
                except Exception:
                    user = AnonymousUser()
            else:
                user = AnonymousUser()

        # 4️⃣ If still anonymous, return empty channels
        if not user.is_authenticated:
            return []

        # 5️⃣ Otherwise return per-user channel
        return [f"user-{user.id}"]
