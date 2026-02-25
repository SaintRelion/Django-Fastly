from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .registry import registry
from .tasks import process_model_task


def setup_model_signals():
    """Attach pre_save/post_save signals to all registered models."""
    for entry in registry.all():
        model = entry["model"]

        # store old values
        @receiver(pre_save, sender=model)
        def cache_old(sender, instance, **kwargs):
            if instance.pk:
                try:
                    old_instance = sender.objects.get(pk=instance.pk)
                    instance._old_instance = old_instance
                except sender.DoesNotExist:
                    instance._old_instance = None
            else:
                instance._old_instance = None

        # handle reactive triggers
        @receiver(post_save, sender=model)
        def handle_triggers(sender, instance, **kwargs):
            triggers = entry.get("triggers", {})
            query_filter = entry.get("query_filter")
            model_label = f"{sender._meta.app_label}.{sender.__name__}"

            # Skip if query filter exists and instance doesn't match
            if (
                query_filter
                and not query_filter(sender.objects.filter(id=instance.id)).exists()
            ):
                return

            # Check triggers
            for field, condition in triggers.items():
                value = getattr(instance, field, None)
                old_value = (
                    getattr(instance._old_instance, field, None)
                    if instance._old_instance
                    else None
                )

                if condition == "boolean":
                    # only fire if changed from False -> True
                    if old_value is not True and value is True:
                        process_model_task.delay(model_label, instance.id)
                elif callable(condition) and condition(value):
                    process_model_task.delay(model_label, instance.id)
