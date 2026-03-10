from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

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

CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOW_CREDENTIALS = True

SR_AUTHENTICATION_MIDDLEWARE = ["corsheaders.middleware.CorsMiddleware"]

AUTHENTICATION_BACKENDS = ["sr_libs.authentication.backends.MultiIdentifierBackend"]

SR_AUTHENTICATION_ACCOUNT_STATUS_MESSAGE = None

SR_AUTHENTICATION_FRONTEND_RESET_PASSWORD_PAGE = None
