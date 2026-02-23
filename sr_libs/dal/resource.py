from django.db import models
from .registry import RESOURCE_REGISTRY, ALLOWED_OPERATIONS


def _normalize_operations(model, operations: dict):
    normalized = {}

    model_fields = [f.name for f in model._meta.fields]

    for op in ALLOWED_OPERATIONS:
        value = operations.get(op, False)

        if value in (False, None):
            normalized[op] = False
            continue

        if value is True or value == "__all__":
            normalized[op] = model_fields
            continue

        if isinstance(value, list):
            invalid = set(value) - set(model_fields)
            if invalid:
                raise ValueError(f"Invalid fields {invalid} for {model.__name__}")
            normalized[op] = value
            continue

        raise ValueError(f"Invalid operation config for '{op}'")

    return normalized


def register_resource(*, name: str, model, endpoint: str, operations: dict):
    if name in RESOURCE_REGISTRY:
        raise ValueError(f"Resource '{name}' already registered.")

    if not issubclass(model, models.Model):
        raise ValueError("model must be a Django model.")

    # Validate fields and operation booleans
    normalized_ops = _normalize_operations(model, operations)

    RESOURCE_REGISTRY[name] = {
        "model": model,
        "endpoint": endpoint,
        "operations": normalized_ops,
    }
