from .context import get_current_user, get_current_ip, get_current_system
from .models import AuditLog


def log_service_action(
    action: str,
    source: str = None,
    category: str = None,
    object_id: str | int | None = None,
    new_data: dict | None = None,
):
    """
    Log a non-CRUD action anywhere in the system (services, scheduled tasks, derived resources).

    Determines the actor automatically:
    - Authenticated user → user + source='user'
    - System context → user=None + source='system:<identity>'
    - No user or system → user=None + source='anonymous'

    source param can override the automatic source.
    """

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
