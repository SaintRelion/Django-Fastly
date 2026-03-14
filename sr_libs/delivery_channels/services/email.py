from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from ..config import SRDeliveryChannelsConfig

SR_DELIVERY_CHANNELS_CONFIG = getattr(
    settings, "SR_DELIVERY_CHANNELS_CONFIG", SRDeliveryChannelsConfig()
)


def send_email(subject: str, message: str, recipient_list: list[str]):
    # ensure credentials exist
    if (
        not SR_DELIVERY_CHANNELS_CONFIG.EMAIL_HOST_USER
        or not SR_DELIVERY_CHANNELS_CONFIG.DEFAULT_FROM_EMAIL
        or not SR_DELIVERY_CHANNELS_CONFIG.EMAIL_HOST_PASSWORD
    ):
        raise ImproperlyConfigured(
            "EMAIL_HOST_USER and DEFAULT_FROM_EMAIL and EMAIL_HOST_PASSWORD must be set to send emails."
        )

    send_mail(
        subject=subject,
        message=message,
        from_email=SR_DELIVERY_CHANNELS_CONFIG.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
