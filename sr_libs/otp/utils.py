from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .config import SROTPConfig
from .models import OTP
import random

SR_OTP_CONFIG = getattr(settings, "SR_OTP_CONFIG", SROTPConfig())


def generate_otp_code(length=6):
    """Generates a numeric OTP code"""
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def create_otp(user, otp_type="sms", extra_info=None):
    ttl = SR_OTP_CONFIG.OTP_EXPIRY_SECONDS

    """Creates an OTP instance"""
    code = generate_otp_code()
    otp = OTP.objects.create(
        user=user,
        code=code,
        type=otp_type,
        expires_at=timezone.now() + timedelta(seconds=ttl),
        additional_info=extra_info or {},
    )
    return otp


def send_otp(user, otp):
    """Send OTP to user using the correct delivery channel."""
    if otp.type == "email":
        from sr_libs.delivery_channels.services.email import send_email

        if not user.email:
            raise ValueError("User has no email.")

        subject = "Your OTP Code"
        message = f"""
Hello {user.username},

Your OTP code is: {otp.code}

This code will expire at {otp.expires_at}.

If you did not request this, please ignore this email.
"""
        send_email(subject, message, [user.email])

    elif otp.type == "sms":
        from sr_libs.delivery_channels.services.sms import send_sms

        if not user.phone_number:
            raise ValueError("User has no phone number.")

        # message = f"Your OTP code is {otp.code}, expires at {otp.expires_at}."
        # TODO: Hardcoded for now
        message = (
            f"Warzone Fiber: Your OTP is {otp.code}.\n"
            "New device login detected. Do not share."
        )
        send_sms(user.phone_number, message)
