from django.db import models
from django.contrib.postgres.fields import JSONField


class ScheduledTask(models.Model):
    model = models.CharField(max_length=255)
    instance_id = models.PositiveIntegerField()
    trigger_field = models.CharField(max_length=255, null=True, blank=True)
    scheduled_at = models.DateTimeField()
    repeat_every = models.DurationField(null=True, blank=True)  # for repeating tasks
    stop_condition = models.JSONField(null=True, blank=True)  # e.g., {"is_paid": true}
    action = models.JSONField(null=True, blank=True)  # optional, define action type
    notification = models.JSONField(
        null=True, blank=True
    )  # optional, define notification type/data
    executed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[("pending", "pending"), ("done", "done"), ("failed", "failed")],
        default="pending",
    )

    class Meta:
        ordering = ["-scheduled_at"]


class Notification(models.Model):
    NOTIFICATION_TYPE_CHOICES = [
        ("in_app", "In-App"),
        ("email", "Email"),
        ("sms", "SMS"),
        ("push", "Push"),
    ]

    model = models.CharField(max_length=255)
    instance_id = models.PositiveIntegerField()
    data = JSONField()
    type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPE_CHOICES, default="email"
    )
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
