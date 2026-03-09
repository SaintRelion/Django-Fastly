from .utils import set_current_ip, set_current_user


class AuditViewSetMixin:
    """
    DRF viewset mixin to set current user/IP for audit logging.
    Place this first in inheritance so it runs initialize_request.
    """

    def initialize_request(self, request, *args, **kwargs):
        request = super().initialize_request(request, *args, **kwargs)
        # JWT auth has already set request.user
        set_current_user(request.user)
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        ip = (
            x_forwarded_for.split(",")[0]
            if x_forwarded_for
            else request.META.get("REMOTE_ADDR")
        )
        set_current_ip(ip)
        return request
