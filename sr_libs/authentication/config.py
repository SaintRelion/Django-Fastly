from dataclasses import dataclass
from datetime import timedelta
from typing import List, Tuple, Optional


@dataclass(frozen=True)
class SRAuthenticationConfig:
    # JWT settings
    ACCESS_TOKEN_LIFETIME: timedelta = timedelta(minutes=30)
    REFRESH_TOKEN_LIFETIME: timedelta = timedelta(days=7)
    ROTATE_REFRESH_TOKENS: bool = True
    BLACKLIST_AFTER_ROTATION: bool = True
    AUTH_HEADER_TYPES: Tuple[str, ...] = ("Bearer",)

    # DRF defaults
    DEFAULT_AUTHENTICATION_CLASSES: List[str] = [
        "sr_libs.authentication.authentication.ContextJWTAuthentication"
    ]
    DEFAULT_PERMISSION_CLASSES: List[str] = [
        "rest_framework.permissions.IsAuthenticated"
    ]
    DEFAULT_RENDERER_CLASSES: List[str] = [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ]

    # Middleware
    MIDDLEWARE: List[str] = ["corsheaders.middleware.CorsMiddleware"]

    # Backends
    AUTHENTICATION_BACKENDS: List[str] = [
        "sr_libs.authentication.backends.MultiIdentifierBackend"
    ]
    IDENTIFIERS: List[str] = ["username", "email"]

    # CORS
    CORS_ALLOW_ALL_ORIGINS: bool = True

    # Optional messages / frontend URLs
    ACCOUNT_STATUS_MESSAGE: Optional[str] = None
    FRONTEND_RESET_PASSWORD_PAGE: Optional[str] = None
