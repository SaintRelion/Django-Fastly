from rest_framework_simplejwt.authentication import JWTAuthentication
from sr_libs.audit_logger.context import set_current_ip, set_current_user


class AuditJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        result = super().authenticate(request)
        if result:
            user, _ = result
            set_current_user(user)

            # Optional: get IP
            ip = request.META.get("REMOTE_ADDR")
            set_current_ip(ip)
        return result
