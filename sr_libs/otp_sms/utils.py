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
