import base64

from rest_framework import status
from webauthn.helpers.options_to_json import options_to_json
from webauthn.helpers.structs import (
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
)

import json

from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import get_user_model

from .models import DeviceCredential, WebAuthnChallenge

from .helpers import (
    create_registration_options,
    verify_registration,
    create_authentication_options,
    verify_authentication,
)

User = get_user_model()


def bytes_to_base64url(b: bytes) -> str:
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()


def base64url_to_bytes(val: str) -> bytes:
    padding = "=" * (-len(val) % 4)
    return base64.urlsafe_b64decode(val + padding)


class CheckDeviceRegistrationView(APIView):
    """
    Check if a user already has WebAuthn device credentials registered.
    """

    permission_classes = []  # or IsAuthenticated if you want login required

    def post(self, request):
        try:
            user = User.objects.get(username=request.data["username"])
        except User.DoesNotExist:
            return Response(
                {"registered": False, "message": "User does not exist"},
                status=status.HTTP_200_OK,
            )

        # Check if user has any registered devices
        has_device = DeviceCredential.objects.filter(user=user).exists()

        return Response({"registered": has_device})


class BeginRegistration(APIView):
    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        options = create_registration_options(user)

        challenge_b64 = bytes_to_base64url(options.challenge)

        WebAuthnChallenge.objects.create(
            user=user,
            challenge=challenge_b64,
            type="registration",
        )

        toJSON = json.loads(options_to_json(options))
        return Response(toJSON)


class FinishRegistration(APIView):
    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        challenge_obj = WebAuthnChallenge.objects.filter(
            user=user, type="registration"
        ).last()

        if not challenge_obj:
            return Response({"error": "No registration challenge found"}, status=400)

        verification = verify_registration(user, challenge_obj.challenge, request.data)

        DeviceCredential.objects.create(
            user=user,
            credential_id=verification.credential_id,
            public_key=verification.credential_public_key,
            sign_count=verification.sign_count,
            device_name=request.data.get("device_name", "Unknown Device"),
        )

        challenge_obj.delete()
        return Response({"status": "registered"})


class BeginLogin(APIView):
    def post(self, request):
        user = User.objects.get(username=request.data["username"])
        creds = DeviceCredential.objects.filter(user=user)

        allow = [
            PublicKeyCredentialDescriptor(
                c.credential_id, PublicKeyCredentialType.PUBLIC_KEY
            )
            for c in creds
        ]

        options = create_authentication_options(allow)
        challenge_b64 = bytes_to_base64url(options.challenge)

        WebAuthnChallenge.objects.create(
            user=user,
            challenge=challenge_b64,
            type="authentication",
        )

        return Response(json.loads(options_to_json(options)))


class FinishLogin(APIView):
    def post(self, request):
        cred = DeviceCredential.objects.filter(
            credential_id=base64url_to_bytes(request.data["rawId"])
        ).first()

        if not cred:
            return Response({"error": "No registered device"}, status=400)

        challenge_obj = WebAuthnChallenge.objects.filter(
            user=cred.user,
            type="authentication",
        ).last()

        if not challenge_obj:
            return Response({"error": "No auth challenge"}, status=400)

        verification = verify_authentication(
            cred,
            challenge_obj.challenge,
            request.data,
        )

        cred.sign_count = verification.new_sign_count
        cred.save(update_fields=["sign_count"])

        challenge_obj.delete()
        return Response({"status": "authenticated"})
