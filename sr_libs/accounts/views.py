from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.hashers import make_password

User = get_user_model()


class RegisterView(APIView):
    permission_classes = []

    def post(self, request):
        data = request.data.copy()
        username = data.get("username")
        password = data.get("password")
        roles = data.pop("roles", [])
        unique_fields = data.pop("uniqueFields", [])

        # Avoid duplicate users for unique fields
        for field in unique_fields:
            if User.objects.filter(**{field: data.get(field)}).exists():
                return Response(
                    {"error": f"User with this {field} already exists"},
                    status=status.HTTP_406_NOT_ACCEPTABLE,
                )

        # Separate User fields from extra_info
        user_fields = {f.name for f in User._meta.get_fields() if f.concrete}
        extra_info = {}
        user_data = {}

        for key, value in data.items():
            if key in user_fields:
                user_data[key] = value
            else:
                extra_info[key] = value

        print("=== User Data ===")
        print(user_data)
        print("=== Extra Data ===")
        print(extra_info)

        # Create the user
        user = User.objects.create(
            **user_data,
            password=make_password(password),
            extra_info=extra_info,  # store everything else here
        )

        # Assign roles → map to Groups
        for role_name in roles:
            group, _ = Group.objects.get_or_create(name=role_name)
            user.groups.add(group)

        return Response(
            {"success": True, "id": user.id}, status=status.HTTP_201_CREATED
        )
