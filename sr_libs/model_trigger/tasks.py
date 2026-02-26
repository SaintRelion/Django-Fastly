from celery import shared_task
from importlib import import_module
from django.apps import apps
from django.utils import timezone
from django.db import transaction
from .models import ScheduledTask
from .registry import registry
import logging

logger = logging.getLogger(__name__)


def resolve_action(action_path: str):
    module_path, func_name = action_path.rsplit(".", 1)
    module = import_module(module_path)
    return getattr(module, func_name)


@shared_task(bind=True, max_retries=5, default_retry_delay=30)
def process_model_task(
    self,
    model_label: str,
    instance_id: int,
    rule_name: str = None,  # Only for scheduled rules
    action_path: str = None,  # Only for reactive rules
    kwargs: dict = None,
):
    kwargs = kwargs or {}

    try:
        Model = apps.get_model(model_label)
        instance = Model.objects.filter(pk=instance_id).first()
        if not instance:
            logger.warning(f"[Task] Instance {instance_id} of {model_label} not found")
            return

        config = registry.get(model_label)
        if not config:
            logger.warning(f"[Task] Model {model_label} not registered")
            return

        rule = None
        # 2️⃣ Scheduled rule path
        if rule_name:
            rule_map = {r.name: r for r in config["scheduled_rules"]}
            rule = rule_map.get(rule_name)
            if not rule:
                logger.warning(f"[Task] Scheduled rule '{rule_name}' not found")
                return
            action_path = rule.action_path

        if not action_path:
            logger.error(f"[Task] No action_path provided for model {model_label}")
            return

        try:
            module_path, func_name = rule.action_path.rsplit(".", 1)
            module = import_module(module_path)
            action = getattr(module, func_name)
            action(instance, **kwargs)
            logger.info(
                f"[Task] Executed action {action_path} for {model_label}#{instance_id}"
            )
        except Exception as exc:
            logger.exception(f"[Task] Action execution failed: {action_path}")
            raise self.retry(exc=exc)

        # Re-fetch instance (important if action changed state)
        instance.refresh_from_db()

        if rule:
            # Check stop condition
            should_stop = False
            if rule.stop_condition:
                try:
                    should_stop = rule.stop_condition(instance)
                except Exception as exc:
                    logger.exception(f"[Task] Stop condition error for {rule_name}")
                    raise self.retry(exc=exc)

            # Get ScheduledTask row
            task = ScheduledTask.objects.filter(
                model=model_label, instance_id=instance_id, rule_name=rule.name
            ).first()
            if not task:
                return

            # Delete or reschedule
            if should_stop:
                task.delete()
                logger.info(f"[Task] '{rule_name}' stopped and deleted")
            elif rule.repeat_every:
                task.scheduled_at = timezone.now() + rule.repeat_every
                task.save()
                logger.info(f"[Task] '{rule_name}' rescheduled to {task.scheduled_at}")
            else:
                task.delete()
                logger.info(f"[Task] '{rule_name}' completed and deleted")
    except Exception as exc:
        logger.exception(
            f"[Task] process_model_task failed for {model_label}#{instance_id}"
        )
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
                rule_name=task.rule_name,
                kwargs=task.kwargs,
            )
