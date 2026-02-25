from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .serializers import create_dynamic_serializer
from .registry import AUTH_REGISTRY


def define_register(*, serializer):
    User = get_user_model()

    # CASE 1 — Custom serializer passed
    if isinstance(serializer, type) and issubclass(serializer, serializers.Serializer):
        AUTH_REGISTRY["register"] = serializer
        return

    # CASE 2 — "__all__" or list of fields
    if serializer == "__all__" or isinstance(serializer, list):
        DynamicSerializer = create_dynamic_serializer(
            resource_model=User,
            allowed_fields=serializer,
            name="DynamicRegisterSerializer",
        )
    else:
        raise ValueError("serializer must be '__all__', list, or Serializer class")

    # Inject create override dynamically
    class RegisterSerializer(DynamicSerializer):
        def create(self, validated_data):
            if "password" in validated_data:
                validated_data["password"] = make_password(validated_data["password"])

            return User.objects.create(**validated_data)

    AUTH_REGISTRY["register"] = RegisterSerializer


def define_me(*, serializer):
    User = get_user_model()

    # CASE 1 — Custom serializer passed
    if isinstance(serializer, type) and issubclass(
        serializer, serializers.BaseSerializer
    ):
        AUTH_REGISTRY["me"] = serializer
        return

    # CASE 2 — "__all__" or list of fields
    if serializer == "__all__" or isinstance(serializer, list):
        DynamicSerializer = create_dynamic_serializer(
            resource_model=User,
            allowed_fields=serializer,
            name="DynamicMeSerializer",
        )
    else:
        raise ValueError("serializer must be '__all__', list, or Serializer class")

    AUTH_REGISTRY["me"] = DynamicSerializer
