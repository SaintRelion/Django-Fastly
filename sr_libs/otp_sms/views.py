from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import OTP
from .utils import create_otp
from django.utils import timezone

User = get_user_model()


class SendOTP(APIView):
    """Send OTP to a user via SMS or Email"""

    def post(self, request):
        username = request.data.get("username")
        otp_type = request.data.get("type", "sms")
        extra_info = request.data.get("extra_info", {})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

        otp = create_otp(user, otp_type, extra_info=extra_info)

        # TODO: integrate SMS/email delivery via Twilio/Semafore
        return Response(
            {"otp_id": otp.id, "expires_at": otp.expires_at, "type": otp.type}
        )


class VerifyOTP(APIView):
    """Verify a submitted OTP code"""

    def post(self, request):
        otp_id = request.data.get("otp_id")
        code = request.data.get("code")

        try:
            otp = OTP.objects.get(id=otp_id)
        except OTP.DoesNotExist:
            return Response(
                {"error": "OTP not found"}, status=status.HTTP_404_NOT_FOUND
            )

        if otp.verified:
            return Response(
                {"error": "OTP already verified"}, status=status.HTTP_400_BAD_REQUEST
            )

        if otp.is_expired():
            return Response(
                {"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        otp.attempt_count += 1
        if otp.code == code:
            otp.verified = True
            otp.save(update_fields=["verified", "attempt_count"])
            return Response({"success": True})
        else:
            otp.save(update_fields=["attempt_count"])
            return Response(
                {"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST
            )
