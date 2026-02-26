from celery import shared_task
from importlib import import_module
from django.apps import apps
from django.utils import timezone
from django.db import transaction
from .models import ScheduledTask
from .registry import registry


def resolve_action(action_path: str):
    module_path, func_name = action_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, func_name)


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def process_model_task(
    self, model_label: str, instance_id: int, action_path: str, kwargs=None
):
    try:
        model = apps.get_model(model_label)
        instance = model.objects.get(id=instance_id)

        action = resolve_action(action_path)
        kwargs = kwargs or {}
        action(instance, **kwargs)

        # Only reschedule AFTER success
        task = ScheduledTask.objects.select_for_update().get(
            model=model_label,
            instance_id=instance_id,
            action_path=action_path,
        )

        if task.repeat_every:
            task.scheduled_at = timezone.now() + task.repeat_every
            task.save(update_fields=["scheduled_at"])
        else:
            task.delete()
    except Exception as exc:
        raise self.retry(exc=exc)


@shared_task
def scan_scheduled_tasks():
    now = timezone.now()

    with transaction.atomic():
        due_tasks = ScheduledTask.objects.select_for_update().filter(
            scheduled_at__lte=now
        )

        for task in due_tasks:
            # Resolve rule to get action_path
            config = registry.get(task.model)
            if not config:
                # skip if model no longer registered
                continue

            rule_map = {r.name: r for r in config["scheduled_rules"]}
            rule = rule_map.get(task.rule_name)
            if not rule:
                # rule removed from code, delete scheduled task
                task.delete()
                continue

            # Execute the action
            process_model_task.delay(
                model_label=task.model,
                instance_id=task.instance_id,
                action_path=rule.action_path,
                kwargs=task.kwargs,
            )
