from rest_framework.permissions import BasePermission
from django.conf import settings


class IsAuditViewer(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        # Check staff/superuser
        if user.is_staff or user.is_superuser:
            return True

        # Check group membership
        allowed_groups = settings.SR_LIBS_AUDIT_LOGGER_ALLOWED_GROUPS
        user_group_names = user.groups.values_list("name", flat=True)
        if any(group in allowed_groups for group in user_group_names):
            return True

        return False
