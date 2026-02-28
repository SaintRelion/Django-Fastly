from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model

from rest_framework_simplejwt.views import TokenObtainPairView
from .models import UserDevice
from sr_libs.authentication.serializers import CustomTokenObtainPairSerializer

from .registry import AUTH_REGISTRY

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class CheckDeviceView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        device_id = request.headers.get("X-Device-ID")

        if not device_id:
            return Response({"error": "No device ID provided"}, status=400)

        try:
            device = UserDevice.objects.get(device_id=device_id)
            return Response({"exists": True, "is_trusted": device.is_trusted})
        except UserDevice.DoesNotExist:
            return Response({"exists": False, "is_trusted": False})


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
