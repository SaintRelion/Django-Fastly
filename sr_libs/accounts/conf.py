from django.conf import settings
from datetime import timedelta

# defaults
DEFAULTS = {
    "JWT_ACCESS_LIFETIME": timedelta(minutes=30),
    "JWT_REFRESH_LIFETIME": timedelta(days=7),
    "JWT_ROTATE_REFRESH_TOKENS": True,
    "JWT_BLACKLIST_AFTER_ROTATION": True,
    "AUTHENTICATION_BACKENDS": [
        "sr_libs.accounts.backends.MultiIdentifierBackend",
    ],
    "AUTH_USER_MODEL": "accounts.User",
    "REST_FRAMEWORK": {
        "DEFAULT_AUTHENTICATION_CLASSES": [
            "rest_framework_simplejwt.authentication.JWTAuthentication",
        ],
        "DEFAULT_PERMISSION_CLASSES": [
            "rest_framework.permissions.IsAuthenticated",
        ],
        "DEFAULT_FILTER_BACKENDS": [
            "django_filters.rest_framework.DjangoFilterBackend",
            "rest_framework.filters.OrderingFilter",
            "rest_framework.filters.SearchFilter",
        ],
        "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
        "PAGE_SIZE": 25,
    },
}

# override with project settings if they exist
for k, v in DEFAULTS.items():
    setattr(settings, k, getattr(settings, k, v))
