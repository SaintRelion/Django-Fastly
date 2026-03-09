from .context import get_current_user, get_current_ip, get_current_system
from .models import AuditLog


def log_service_action(
    action, source=None, model_name=None, object_id=None, extra=None
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

    # override source if explicitly provided
    if source:
        resolved_source = source

    AuditLog.objects.create(
        user=user,
        source=resolved_source,
        model_name=model_name,
        object_id=object_id,
        action=action,
        new_data=extra,
        ip_address=ip,
    )
