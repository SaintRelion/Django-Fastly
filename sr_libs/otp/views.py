from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from django.contrib.auth import get_user_model

from ..delivery_channels.services.email import send_email
from .models import OTP
from .utils import create_otp, send_otp

User = get_user_model()


class SendOTP(APIView):
    """Send OTP to a user via SMS or Email"""

    permission_classes = []

    def post(self, request):
        identifier = request.data.get("username") or request.data.get("email")

        if not identifier:
            return Response({"detail": "Username or email required."}, status=400)

        otp_type = request.data.get("otp_type", "sms")
        extra_info = request.data.get("extra_info", {})

        try:
            user = User.objects.get(Q(username=identifier) | Q(email=identifier))
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=404)

        otp = create_otp(user, otp_type, extra_info=extra_info)
        try:
            send_otp(user, otp)
        except ValueError as e:
            return Response({"detail": str(e)}, status=400)

        return Response(
            {
                "otp_id": otp.id,
                "expires_at": otp.expires_at,
                "type": otp.type,
                "detail": "OTP sent successfully.",
            }
        )


class VerifyOTP(APIView):
    """Verify a submitted OTP code"""

    permission_classes = []

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
