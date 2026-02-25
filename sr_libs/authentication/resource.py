from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.hashers import make_password

from .serializers import create_dynamic_serializer
from .registry import AUTH_REGISTRY


def define_register(
    *,
    serializer,
    auto_hash_password=True,
    password_field="password",
    read_only_fields=[]
):
    User = get_user_model()

    # CASE 1 — Custom serializer passed
    if isinstance(serializer, type) and issubclass(serializer, serializers.Serializer):
        AUTH_REGISTRY["register"] = serializer
        return

    # CASE 2 — "__all__"
    if serializer == "__all__":
        fields = "__all__"
    elif isinstance(serializer, list):
        fields = serializer
    else:
        raise ValueError("serializer must be '__all__', list, or Serializer class")

    DynamicSerializer = create_dynamic_serializer(
        accounts_model=User,
        allowed_fields=fields,
        name="DynamicRegisterSerializer",
        allowed_read_only_fields=["id"] + read_only_fields,
    )

    # Inject create override dynamically
    class RegisterSerializer(DynamicSerializer):
        def create(self, validated_data):
            if auto_hash_password and password_field in validated_data:
                validated_data[password_field] = make_password(
                    validated_data[password_field]
                )

            return User.objects.create(**validated_data)

    AUTH_REGISTRY["register"] = RegisterSerializer


def define_me(*, serializer):
    User = get_user_model()

    # Custom serializer
    if isinstance(serializer, type) and issubclass(serializer, serializers.Serializer):
        AUTH_REGISTRY["me"] = serializer
        return

    if serializer == "__all__":
        fields = "__all__"
    elif isinstance(serializer, list):
        fields = serializer
    else:
        raise ValueError("serializer must be '__all__', list, or Serializer class")

    DynamicSerializer = create_dynamic_serializer(
        accounts_model=User,
        allowed_fields=fields,
        name="DynamicMeSerializer",
        allowed_read_only_fields=[],
    )

    AUTH_REGISTRY["me"] = DynamicSerializer
