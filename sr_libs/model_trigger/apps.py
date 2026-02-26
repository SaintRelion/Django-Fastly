from django.apps import AppConfig


class ModelTriggerConfig(AppConfig):
    name = "sr_libs.model_trigger"

    def ready(self):
        from .signals import setup_model_signals

        setup_model_signals()
