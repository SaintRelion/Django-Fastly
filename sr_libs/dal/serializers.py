from rest_framework import serializers


def create_dynamic_serializer(resource_model, allowed_fields, name):
    class Meta:
        model = resource_model
        fields = allowed_fields
        read_only_fields = ["id", "created_at"]

    attrs = {"Meta": Meta}

    return type(name, (serializers.ModelSerializer,), attrs)
