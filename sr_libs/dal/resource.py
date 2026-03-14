from typing import Callable, Optional

from django.db import models
from rest_framework import serializers

from .serializers import DerivedSerializer

from .types import AuthenticatorsDict, OperationsDict, PermissionValue, PermissionsDict
from .registry import RESOURCE_REGISTRY, DERIVED_RESOURCE_REGISTRY


def register_resource(
    *,
    name: str,
    model: type[models.Model],
    operations: OperationsDict,
    authenticators: Optional[AuthenticatorsDict] = None,
    permissions: Optional[PermissionsDict] = None,
    filterset_fields: Optional[list[str]] = None,
):
    if name in RESOURCE_REGISTRY:
        raise ValueError(f"Resource '{name}' already registered.")

    if not issubclass(model, models.Model):
        raise ValueError("model must be a Django model.")

    # default: all model fields if filterset_fields is None
    if filterset_fields is None:
        filterset_fields = [f.name for f in model._meta.fields]

    RESOURCE_REGISTRY[name] = {
        "model": model,
        "endpoint": name,
        "operations": operations,
        "authenticators": authenticators or {},
        "permissions": permissions or {},
        "filterset_fields": filterset_fields,
    }


def register_derived_resource(
    *,
    name: str,
    serializer: type[DerivedSerializer],
    permissions: PermissionValue = None,
):
    if not (isinstance(serializer, type) and issubclass(serializer, DerivedSerializer)):
        raise ValueError("Derived resource requires a DerivedSerializer class")

    DERIVED_RESOURCE_REGISTRY[name] = {
        "endpoint": name,
        "serializer": serializer,
        "permissions": permissions or [],
    }
