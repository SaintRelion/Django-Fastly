from rest_framework import serializers


def create_dynamic_serializer(resource_model, operation_fields, name):
    class Meta:
        model = resource_model
        fields = operation_fields

    attrs = {"Meta": Meta}

    return type(name, (serializers.ModelSerializer,), attrs)
