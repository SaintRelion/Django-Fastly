from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.contrib.auth import authenticate, get_user_model

from rest_framework_simplejwt.views import TokenObtainPairView
from .models import UserDevice
from sr_libs.authentication.serializers import CustomTokenObtainPairSerializer

from .registry import AUTH_REGISTRY

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CheckDeviceView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        device_id = (data.get("identifier") or "").strip()
        username = (data.get("username") or "").strip()
        password = data.get("password") or ""

        if not device_id or not username or not password:
            return Response(
                {"error": "identifier, username, and password required"}, status=400
            )

        # Validate user credentials
        user = authenticate(username=username, password=password)
        if user is None:
            return Response({"exists": False, "is_trusted": False, "valid_user": False})

        device = UserDevice.objects.filter(user=user, device_id=device_id).first()

        if device is not None:
            return Response(
                {
                    "is_trusted": device.is_trusted,
                    "valid_user": True,
                    "device_id": device.device_id,
                }
            )

        # device not found
        return Response(
            {
                "is_trusted": False,
                "valid_user": True,  # user credentials were valid
                "device_id": device_id,
            }
        )


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer_class = AUTH_REGISTRY.get("register")

        if not serializer_class:
            return Response(
                {"error": "Register serializer not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = serializer_class(
            data=request.data,
            context={"request": request},
        )

        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {"id": user.id},
            status=status.HTTP_201_CREATED,
        )


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer_class = AUTH_REGISTRY.get("me")

        if not serializer_class:
            return Response(
                {"error": "Me serializer not configured."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        serializer = serializer_class(request.user)

        return Response(serializer.data)
