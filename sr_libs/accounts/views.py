from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from django.conf import settings
from django.contrib.auth import get_user_model

from sr_libs.accounts.registry import AUTH_REGISTRY

User = get_user_model()


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
