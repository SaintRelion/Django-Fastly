from rest_framework import serializers


def create_dynamic_serializer(
    accounts_model,
    allowed_fields,
    name,
    allowed_read_only_fields=None,
):
    allowed_read_only_fields = allowed_read_only_fields or []

    class Meta:
        model = accounts_model
        fields = allowed_fields
        read_only_fields = allowed_read_only_fields

    attrs = {"Meta": Meta}

    return type(name, (serializers.ModelSerializer,), attrs)
