import requests
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


def send_sms(phone_number, message):
    if not settings.SEMAPHORE_API_KEY or not settings.SEMAPHORE_SMS_SENDER_NAME:
        raise ImproperlyConfigured(
            "EMAIL_HOST_USER and SEMAPHORE_SMS_SENDER_NAME must be set to send emails."
        )

    payload = {
        "apikey": settings.SEMAPHORE_API_KEY,
        "sendername": settings.SEMAPHORE_SMS_SENDER_NAME,
        "message": message,
        "number": phone_number,
    }

    response = requests.post(
        "https://semaphore.co/api/v4/messages",
        data=payload,
    )

    response.raise_for_status()
    return True
