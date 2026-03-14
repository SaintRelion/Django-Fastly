from django.conf import settings
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q
from django.contrib.auth import get_user_model

from .config import SRAuthenticationConfig

User = get_user_model()

AUTH_CONFIG = getattr(settings, "SR_AUTHENTICATION_CONFIG", SRAuthenticationConfig())


class MultiIdentifierBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Dynamically build Q object from configured identifiers
            query = Q()
            for field in AUTH_CONFIG.IDENTIFIERS:
                kwargs = {field: username}
                query |= Q(**kwargs)

            user = User.objects.get(query)
        except User.DoesNotExist:
            return None

        if user.check_password(password):
            return user
        return None
