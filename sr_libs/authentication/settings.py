from datetime import timedelta

CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True

MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"]

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

AUTHENTICATION_BACKENDS = ["sr_libs.authentication.backends.MultiIdentifierBackend"]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ],
    # # May transfer to DAL
    # "DEFAULT_FILTER_BACKENDS": [
    #     "django_filters.rest_framework.DjangoFilterBackend",
    #     "rest_framework.filters.OrderingFilter",
    #     "rest_framework.filters.SearchFilter",
    # ],
    # "DEFAULT_PAGINATION_CLASS": "core.pagination.DefaultPagination",
    # "PAGE_SIZE": 25,
}

try:
    from django_eventstream.renderers import (
        SSEEventRenderer,
        BrowsableAPIEventStreamRenderer,
    )

    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"].extend(
        [
            "django_eventstream.renderers.SSEEventRenderer",
            "django_eventstream.renderers.BrowsableAPIEventStreamRenderer",
        ]
    )
except ImportError:
    pass
