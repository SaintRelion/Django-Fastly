from django_eventstream.viewsets import EventsViewSet
from rest_framework.permissions import AllowAny


class MyEventsViewSet(EventsViewSet):
    permission_classes = [AllowAny]

    # Channels can be dynamic based on request.user
    def get_channels(self, request=None, *args, **kwargs):
        # If request is missing or user is not authenticated, return empty list
        if (
            not request
            or not getattr(request, "user", None)
            or not request.user.is_authenticated
        ):
            return []

        # Otherwise return per-user channel
        return [f"user-{request.user.id}"]
