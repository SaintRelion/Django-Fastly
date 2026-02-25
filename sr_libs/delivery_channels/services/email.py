from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


def send_email(subject: str, message: str, recipient_list: list[str]):
    # ensure credentials exist
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        raise ImproperlyConfigured(
            "EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set to send emails."
        )

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=recipient_list,
        fail_silently=False,
    )
