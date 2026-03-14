from sr_libs.authentication.context import (
    get_current_user,
    get_current_ip,
    get_current_system,
)
from .models import AuditLog


def log_service_action(
    action: str,
    source: str = None,
    category: str = None,
    object_id: str | int | None = None,
    new_data: dict | None = None,
):
    user = get_current_user()
    system_identity = get_current_system()
    ip = get_current_ip()

    if user and getattr(user, "is_authenticated", False):
        resolved_source = "user"
    elif system_identity:
        resolved_source = f"system:{system_identity}"
        user = None
    else:
        resolved_source = "anonymous"
        user = None

    # If caller explicitly provides a source, override
    if source:
        resolved_source = source

    AuditLog.objects.create(
        user=user,
        source=resolved_source,
        category=category,
        action=action,
        object_id=str(object_id) if object_id is not None else None,
        new_data=new_data,
        ip_address=ip,
    )
