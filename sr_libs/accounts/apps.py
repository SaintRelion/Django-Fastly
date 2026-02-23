from django.apps import AppConfig
from django.conf import settings


class AccountsConfig(AppConfig):
    name = "sr_libs.accounts"

    def ready(self):
        required_apps = [
            "rest_framework",
            "rest_framework_simplejwt",
            "rest_framework_simplejwt.token_blacklist",
        ]

        for app in required_apps:
            if app not in settings.INSTALLED_APPS:
                settings.INSTALLED_APPS.append(app)
