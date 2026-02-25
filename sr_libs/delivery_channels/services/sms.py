from twilio.rest import Client
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


def send_sms(to: str, message: str):
    """Send an SMS using Twilio."""
    if not (
        settings.TWILIO_ACCOUNT_SID
        and settings.TWILIO_AUTH_TOKEN
        and settings.TWILIO_PHONE_NUMBER
    ):
        raise ImproperlyConfigured(
            "TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER must be set to send SMS."
        )

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=to,
    )
