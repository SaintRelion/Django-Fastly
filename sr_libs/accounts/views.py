from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data
        username = data.get("username")
        password = data.get("password")
        extra_info = data.get("extra_info", {})

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "User already exists"}, status=status.HTTP_406_NOT_ACCEPTABLE
            )

        user = User.objects.create(
            username=username, password=make_password(password), extra_info=extra_info
        )

        return Response(
            {"success": True, "id": user.id}, status=status.HTTP_201_CREATED
        )
