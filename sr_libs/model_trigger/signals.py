from django.db.models.signals import post_save
from django.db import transaction
from django.dispatch import receiver

from .models import ScheduledTask
from .registry import registry


def setup_model_signals():
    for entry in registry.all():
        model = entry["model"]
        model_label = f"{model._meta.app_label}.{model.__name__}"

        @receiver(post_save, sender=model)
        def handle_post_save(
            sender, instance, created, model_label=model_label, **kwargs
        ):
            config = registry.get(model_label)
            if not config:
                return

            # --- 1️⃣ Reactive rules ---
            # always run immediately inside transaction
            for rule in config["reactive_rules"]:
                rule.action(instance, created)

            # --- 2️⃣ Scheduled rules ---
            # defer scheduling until transaction commits
            def schedule_tasks():
                for rule in config["scheduled_rules"]:
                    should_monitor = rule.monitor_condition(instance)
                    existing_task = ScheduledTask.objects.filter(
                        model=model_label,
                        instance_id=instance.id,
                        rule_name=rule.name,
                    ).first()

                    if should_monitor and not existing_task:
                        scheduled_at = rule.scheduled_at(instance)
                        ScheduledTask.objects.create(
                            model=model_label,
                            instance_id=instance.id,
                            rule_name=rule.name,
                            scheduled_at=scheduled_at,
                            repeat_every=rule.repeat_every,
                            status="pending",
                        )
                    elif existing_task and (
                        not should_monitor
                        or (rule.stop_condition and rule.stop_condition(instance))
                    ):
                        existing_task.delete()

            transaction.on_commit(schedule_tasks)
