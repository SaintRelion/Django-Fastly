from django_eventstream import EventStreamView
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class UserEventStreamView(EventStreamView):
    def get_channels(self):
        user = self.request.user
        if not user.is_authenticated:
            return []

        return [f"user-{user.id}"]
