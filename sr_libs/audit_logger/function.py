from .models import AuditLog
from .utils import get_current_user, get_client_ip

def log_service_action(action, source="system", model_name=None, object_id=None, extra=None):
    """Call this anywhere for non-CRUD services like OTP, reports, etc."""
    AuditLog.objects.create(
        user=get_current_user(),
        source=source,
        model_name=model_name,
        object_id=object_id,
        action=action,
        new_data=extra,
        ip_address=get_client_ip()
    )