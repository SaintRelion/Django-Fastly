from django.utils import timezone
from datetime import timedelta
from .models import OTP
import random


def generate_otp_code(length=6):
    """Generates a numeric OTP code"""
    return "".join(str(random.randint(0, 9)) for _ in range(length))


def create_otp(user, otp_type="sms", ttl_seconds=300, extra_info=None):
    """Creates an OTP instance"""
    code = generate_otp_code()
    otp = OTP.objects.create(
        user=user,
        code=code,
        type=otp_type,
        expires_at=timezone.now() + timedelta(seconds=ttl_seconds),
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

        message = f"Your OTP code is {otp.code}, expires at {otp.expires_at}."
        send_sms(user.phone_number, message)
