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
    self,
    model_label,
    instance_id,
    rule_name,
    action_path,
    kwargs=None,
):
    try:
        Model = apps.get_model(model_label)
        instance = Model.objects.filter(pk=instance_id).first()
        if not instance:
            return

        config = registry.get(model_label)
        if not config:
            return

        rule_map = {r.name: r for r in config["scheduled_rules"]}
        rule = rule_map.get(rule_name)
        if not rule:
            return

        # 1️⃣ Execute action
        action = import_module(action_path)
        action(instance, **kwargs)

        # 2️⃣ Re-fetch instance (important if action changed state)
        instance.refresh_from_db()

        # 3️⃣ Evaluate stop condition
        should_stop = False
        if rule.stop_condition:
            should_stop = rule.stop_condition(instance)

        # 4️⃣ Get ScheduledTask row
        task = ScheduledTask.objects.filter(
            model=model_label, instance_id=instance_id, rule_name=rule.name
        ).first()

        if not task:
            return

        # 5️⃣ If stop condition met → delete task
        if should_stop:
            task.delete()
            return

        # 6️⃣ Otherwise reschedule if repeat_every exists
        if rule.repeat_every:
            task.scheduled_for = timezone.now() + rule.repeat_every
            task.save()
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
