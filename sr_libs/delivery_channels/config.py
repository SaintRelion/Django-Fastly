from dataclasses import dataclass, field
from typing import List, Optional, Dict, Union


@dataclass(frozen=True)
class SRDeliveryChannelsConfig:
    # Twilio SMS configuration
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None

    # SMS (other provider)
    SEMAPHORE_API_KEY: Optional[str] = None
    SEMAPHORE_SMS_SENDER_NAME: Optional[str] = None

    # Email configuration
    EMAIL_BACKEND: str = "django.core.mail.backends.smtp.EmailBackend"
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587
    EMAIL_USE_TLS: bool = True

    EMAIL_HOST_USER: Optional[str] = None
    EMAIL_HOST_PASSWORD: Optional[str] = None
    DEFAULT_FROM_EMAIL: Optional[str] = None  # Usually same as EMAIL_HOST_USER

    # Live / EventStream
    EVENTSTREAM_CHANNELMANAGER_CLASS: str = (
        "sr_libs.delivery_channels.managers.channelmanager.MyChannelManager"
    )
    EVENTSTREAM_REDIS: Dict[str, Union[int, str]] = field(default_factory=dict)
    EVENTSTREAM_DEFAULT_RENDERERS: List[str] = field(
        default_factory=lambda: [
            "django_eventstream.renderers.SSEEventRenderer",
            "django_eventstream.renderers.BrowsableAPIEventStreamRenderer",
        ]
    )
