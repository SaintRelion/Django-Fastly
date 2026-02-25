from django.apps import AppConfig


class NotificationConfig(AppConfig):
    name = "sr_libs.notifications"

    def ready(self):
        from .signals import setup_model_signals

        setup_model_signals()
