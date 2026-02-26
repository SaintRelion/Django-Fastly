from celery import shared_task
from django.apps import apps
from importlib import import_module
from django.utils import timezone
from .models import ScheduledTask
from .registry import registry


def resolve_action(action_path: str):
    """
    Import and return callable from string path, e.g. "billing.actions.send_sms"
    """
    module_path, func_name = action_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, func_name)


@shared_task(bind=True)
def process_model_task(
    self, model_label: str, instance_id: int, action_path: str, kwargs=None
):
    """
    Execute the action associated with a reactive or scheduled rule.
    """
    model = apps.get_model(model_label)
    instance = model.objects.get(id=instance_id)

    action = resolve_action(action_path)
    kwargs = kwargs or {}
    action(instance, **kwargs)


@shared_task
def scan_scheduled_tasks():
    """
    Celery Beat task: scan ScheduledTask table and execute due tasks
    """
    now = timezone.now()
    due_tasks = ScheduledTask.objects.filter(scheduled_at__lte=now)

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

        # Update or remove ScheduledTask
        if task.repeat_every:
            task.scheduled_at += task.repeat_every
            task.save()
        else:
            task.delete()
