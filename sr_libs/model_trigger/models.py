from datetime import datetime, timedelta

from django.db import models
from dataclasses import dataclass, field
from typing import Callable, Optional, Dict, Any


@dataclass
class ReactiveRule:
    name: str  # optional, for clarity
    condition: Callable[[Any, bool], bool]  # (instance, created) -> bool
    action_path: str  # e.g., "billing.actions.send_sms"
    kwargs: Optional[Dict[str, Any]] = field(default_factory=dict)


@dataclass
class ScheduledRule:
    name: str  # unique identifier for this rule
    monitor_condition: Callable[[Any], bool]  # should we monitor this instance?
    scheduled_at: Callable[[Any], datetime]  # when to schedule first run
    action_path: str
    repeat_every: Optional[timedelta] = None
    stop_condition: Optional[Callable[[Any], bool]] = None
    kwargs: Optional[Dict[str, Any]] = field(default_factory=dict)


class ScheduledTask(models.Model):
    model = models.CharField(max_length=255)
    instance_id = models.PositiveIntegerField()

    rule_name = models.CharField(max_length=100)

    scheduled_at = models.DateTimeField()
    repeat_every = models.DurationField(null=True, blank=True)

    status = models.CharField(
        max_length=15,
        choices=[
            ("pending", "pending"),
            ("done", "done"),
        ],
        default="pending",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_at"]
        indexes = [
            models.Index(fields=["status", "scheduled_at"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["model", "instance_id", "rule_name"],
                name="unique_scheduled_rule_per_instance",
            )
        ]
