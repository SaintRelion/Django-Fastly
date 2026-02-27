from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ScheduledTask
from .registry import registry
from .tasks import process_model_task


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
            for rule in config["reactive_rules"]:
                print("==========================Reacting")
                if rule.condition(instance, created):
                    process_model_task.delay(
                        model_label=model_label,
                        instance_id=instance.id,
                        action_path=rule.action_path,
                        kwargs=rule.kwargs,
                    )

            # --- 2️⃣ Scheduled rules ---
            for rule in config["scheduled_rules"]:
                # Check if we should monitor this instance
                # TODO: WTF HAHAHAH FIX THIS SHIT
                print("==========================Scheduling")
                should_monitor = rule.monitor_condition(instance)
                print(should_monitor)
                existing_task = ScheduledTask.objects.filter(
                    model=model_label,
                    instance_id=instance.id,
                    rule_name=rule.name,
                ).first()

                if should_monitor:
                    # Create ScheduledTask if it doesn't exist
                    scheduled_at = rule.scheduled_at(instance)
                    if not existing_task:
                        ScheduledTask.objects.create(
                            model=model_label,
                            instance_id=instance.id,
                            rule_name=rule.name,
                            scheduled_at=scheduled_at,
                            repeat_every=rule.repeat_every,
                            status="pending",
                        )
                else:
                    # Stop condition met → delete scheduled task
                    if (
                        existing_task
                        and rule.stop_condition
                        and rule.stop_condition(instance)
                    ):
                        existing_task.delete()
                    elif existing_task and not rule.stop_condition:
                        # optional: delete if monitor_condition False and no stop_condition
                        existing_task.delete()
