from django.core.mail import send_mail
from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


def send_email_otp(user, otp):
    # ensure credentials exist
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        raise ImproperlyConfigured(
            "EMAIL_HOST_USER and EMAIL_HOST_PASSWORD must be set to send emails."
        )

    subject = "Your OTP Code"
    message = f"""
Hello {user.username},

Your OTP code is: {otp.code}

This code will expire at {otp.expires_at}.

If you did not request this, please ignore this email.
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )
