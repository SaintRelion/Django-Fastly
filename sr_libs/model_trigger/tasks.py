from celery import shared_task
from django.apps import apps
from .models import Notification, ScheduledTask
from .registry import registry
from django.utils import timezone
from sr_libs.delivery_channels.services.email import send_email
from sr_libs.delivery_channels.services.sms import send_sms

SERVICE_MAP = {
    "in_app": None,
    "email": send_email,
    "sms": send_sms,
}


@shared_task(bind=True, max_retries=3)
def process_model_task(self, model_label, instance_id):
    """Process a single reactive or scheduled task."""
    reg_entry = registry.get(model_label)
    if not reg_entry:
        return

    model = apps.get_model(model_label)
    try:
        instance = model.objects.get(id=instance_id)
    except model.DoesNotExist:
        return

    # Resolve data for notification
    resolver = reg_entry.get("resolver")
    data = resolver(instance) if resolver else {}

    # Create notification if needed
    notification_type = reg_entry.get("notification_type", "in_app")
    Notification.objects.create(
        model=model_label, instance_id=instance_id, data=data, type=notification_type
    )

    # Send via delivery channel
    service = SERVICE_MAP.get(notification_type)
    if service:
        if notification_type == "email":
            recipient = data.get("user_email")
            if recipient:
                service(
                    subject=data.get("subject", "Notification"),
                    message=data.get("message", ""),
                    recipient_list=[recipient],
                )
        elif notification_type == "sms":
            recipient = data.get("user_phone")
            if recipient:
                service(recipient, data.get("message", ""))


@shared_task
def scan_scheduled_tasks():
    """Scan all scheduled tasks and enqueue those ready to run."""
    now = timezone.now()
    for entry in registry.all():
        scheduled = entry.get("scheduled")
        if not scheduled:
            continue

        model_label = f"{entry['model']._meta.app_label}.{entry['model'].__name__}"
        # iterate instances
        model = entry["model"]
        qs = model.objects.all()
        for instance in qs:
            # compute scheduled_at from callable or fixed datetime
            sched_time = scheduled.get("scheduled_at")
            if callable(sched_time):
                scheduled_at = sched_time(instance)
            else:
                scheduled_at = sched_time

            if scheduled_at <= now:
                stop_condition = scheduled.get("stop_condition")
                if stop_condition:
                    # skip if stop_condition met
                    if all(
                        getattr(instance, k) == v for k, v in stop_condition.items()
                    ):
                        continue

                # create ScheduledTask record
                st, created = ScheduledTask.objects.get_or_create(
                    model=model_label,
                    instance_id=instance.id,
                    scheduled_at=scheduled_at,
                    defaults={
                        "notification": scheduled.get("notification"),
                        "action": scheduled.get("action"),
                        "status": "pending",
                    },
                )
                # enqueue for execution
                process_model_task.delay(model_label, instance.id)

                # update for repeat
                repeat = scheduled.get("repeat_every")
                if repeat:
                    st.scheduled_at = scheduled_at + repeat
                    st.save()
