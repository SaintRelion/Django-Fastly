from django.db import models
from rest_framework import serializers
from .registry import RESOURCE_REGISTRY, DERIVED_RESOURCE_REGISTRY


def register_resource(*, name: str, model, operations: dict):
    if name in RESOURCE_REGISTRY:
        raise ValueError(f"Resource '{name}' already registered.")

    if not issubclass(model, models.Model):
        raise ValueError("model must be a Django model.")

    RESOURCE_REGISTRY[name] = {
        "model": model,
        "endpoint": name,
        "operations": operations,
    }


def register_derived_resource(*, name: str, serializer, operations: dict = None):
    operations = operations or {"list": True}

    # Validate operations
    for op in operations.keys():
        if op not in {"list"}:
            raise ValueError(f"Derived resources only support 'list', not '{op}'")

    if not (
        isinstance(serializer, type)
        and issubclass(serializer, serializers.BaseSerializer)
    ):
        raise ValueError("Derived resource requires a DRF Serializer class")

    DERIVED_RESOURCE_REGISTRY[name] = {
        "endpoint": name,
        "serializer": serializer,
        "operations": operations,
    }
