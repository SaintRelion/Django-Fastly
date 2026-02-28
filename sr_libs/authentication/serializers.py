from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

from sr_libs.authentication.models import UserDevice


def create_dynamic_serializer(
    accounts_model=None, allowed_fields="__all__", custom_serializer=None
):
    if custom_serializer:
        return custom_serializer  # use custom serializer directly

    if accounts_model is None:
        raise ValueError("Either resource_model or custom_serializer must be provided.")

    if allowed_fields == "__all__":
        allowed_fields = [f.name for f in accounts_model._meta.fields]

    model_field_names = {f.name for f in accounts_model._meta.fields}
    _read_only_fields = ["id"]  # always include id
    for f in ["created_at", "updated_at"]:
        if f in model_field_names:
            _read_only_fields.append(f)

    class Meta:
        model = accounts_model
        fields = allowed_fields
        read_only_fields = _read_only_fields

    attrs = {"Meta": Meta}

    return type(
        f"{accounts_model.__name__}Serializer",
        (serializers.ModelSerializer,),
        attrs,
    )


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        request = self.context.get("request")
        user = self.user

        if request and user:
            device_id = request.headers.get("X-Device-ID")
            user_agent = request.META.get("HTTP_USER_AGENT")
            ip_address = request.META.get("REMOTE_ADDR")

            if device_id:
                UserDevice.objects.update_or_create(
                    user=user,
                    device_id=device_id,
                    defaults={
                        "user_agent": user_agent,
                        "ip_address": ip_address,
                        "is_trusted": True,
                    },
                )

        return data
