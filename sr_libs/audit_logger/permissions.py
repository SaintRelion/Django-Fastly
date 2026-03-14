from rest_framework.permissions import BasePermission
from django.conf import settings
from .config import SRAuditLoggerConfig

SR_AUDIT_LOGGER_CONFIG = getattr(
    settings, "SR_AUDIT_LOGGER_CONFIG", SRAuditLoggerConfig()
)


class IsAuditViewer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Check staff/superuser
        if user.is_staff or user.is_superuser:
            return True

        # Check group membership
        user_group_names = user.groups.values_list("name", flat=True)

        if any(
            group in SR_AUDIT_LOGGER_CONFIG.ALLOWED_GROUPS for group in user_group_names
        ):
            return True

        return False
