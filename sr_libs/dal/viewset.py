from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, viewsets
from rest_framework.exceptions import MethodNotAllowed
from django.db import models

import django_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.settings import api_settings

from .serializers import create_dynamic_serializer
from .mixins import ArchiveMixin

ACTION_MAP = {
    "list": "list",
    "retrieve": "retrieve",
    "create": "create",
    "update": "update",
    "partial_update": "update",
    "destroy": "delete",
}


def map_request_to_action(request, kwargs):
    method = request.method.lower()
    if method == "get":
        return "retrieve" if "pk" in kwargs else "list"
    elif method == "post":
        return "create"
    elif method in ["put", "patch"]:
        return "update"
    elif method == "delete":
        return "delete"
    return None


def create_dynamic_filterset(model: type[models.Model]):
    """
    Auto-generate a FilterSet class for a model.
    Supports:
      - exact lookups for all fields
      - contains for CharFields/TextFields
      - in, gte, lte for numeric fields
    """
    fields_dict = {}

    for f in model._meta.get_fields():
        if isinstance(f, models.Field):
            field_name = f.name
            lookups = ["exact"]  # always support exact

            if isinstance(f, (models.CharField, models.TextField, models.EmailField)):
                lookups.append("contains")
                lookups.append("in")
            elif isinstance(
                f,
                (
                    models.IntegerField,
                    models.FloatField,
                    models.DecimalField,
                    models.DateField,
                    models.DateTimeField,
                ),
            ):
                lookups.extend(["gte", "lte", "in"])
            elif isinstance(f, models.BooleanField):
                pass  # only exact

            fields_dict[field_name] = lookups

    # Dynamically create a FilterSet class
    return type(
        f"{model.__name__}DynamicFilterSet",
        (django_filters.FilterSet,),
        {
            "Meta": type(
                "Meta",
                (),
                {
                    "model": model,
                    "fields": fields_dict,
                },
            )
        },
    )


def create_resource_viewset(name, config):
    model = config["model"]
    operations = config["operations"]

    DynamicFilterSet = create_dynamic_filterset(model)

    class ResourceViewSet(viewsets.ModelViewSet):
        queryset = model.objects.all()
        serializer_class = None  # dynamic
        filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        filterset_class = DynamicFilterSet
        filterset_fields = config.get("filterset_fields") or "__all__"
        search_fields = config.get("search_fields") or "__all__"
        ordering_fields = config.get("ordering_fields") or "__all__"

        def get_action(self):
            return map_request_to_action(self.request, self.kwargs)

        def get_authenticators(self):
            action = self.get_action()

            auth_config = config.get("authenticators", {}).get(action)
            # [] → disable authentication
            if auth_config == []:
                return []

            # default DRF authenticators
            return super().get_authenticators()

        def get_permissions(self):
            action = self.get_action()

            perms = config.get("permissions", {}).get(action)
            if perms:
                return [p() for p in perms]

            return [IsAuthenticated()]

        def get_queryset(self):
            qs = super().get_queryset()

            # Archive logic
            if hasattr(model, "is_archived") and operations.get("archive"):
                include_archived = self.request.query_params.get("is_archived")
                if include_archived is None or include_archived.lower() == "false":
                    qs = qs.filter(is_archived=False)
                elif include_archived.lower() == "true":
                    qs = qs.filter(is_archived=True)
                elif include_archived.lower() == "trulse":
                    pass  # literally all rows

            # Handle __ne filters manually
            ne_filters = {
                k: v for k, v in self.request.query_params.items() if k.endswith("__ne")
            }
            for key, value in ne_filters.items():
                # Strip the __ne suffix
                field_name = key[:-4]

                # Use exclude(), supports related fields
                qs = qs.exclude(**{field_name: value})

            return qs

        def get_serializer_class(self):
            drf_action = self.action
            dal_action = ACTION_MAP.get(drf_action)

            if not dal_action:
                raise MethodNotAllowed(f"{drf_action} not supported")

            op_value = operations.get(dal_action)
            if op_value is False or op_value is None:
                raise MethodNotAllowed(f"{dal_action} not allowed")

            if op_value is True:
                op_value = "__all__"

            # CASE 1: Custom serializer class
            if isinstance(op_value, type) and issubclass(
                op_value, serializers.BaseSerializer
            ):
                return op_value

            # CASE 2 & 3: list of fields or "__all__"
            return create_dynamic_serializer(
                resource_model=model,
                allowed_fields=op_value,
            )

        def destroy(self, request, *args, **kwargs):
            if not operations.get("delete"):
                raise MethodNotAllowed("Delete not allowed")

            return super().destroy(request, *args, **kwargs)

        def perform_destroy(self, instance):
            if operations.get("archive"):
                if not isinstance(instance, ArchiveMixin):
                    raise ValueError(
                        f"{name.capitalize()} must inherit ArchiveMixin for archive support."
                    )
                instance.is_archived = True
                instance.save()
            else:
                super().perform_destroy(instance)

    ResourceViewSet.__name__ = f"{name.capitalize()}ViewSet"

    return ResourceViewSet


def create_derived_viewset(name, config):
    serializer_class = config["serializer"]
    permissions = config.get("permissions", [])

    class DerivedViewSet(viewsets.ViewSet):
        filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        filterset_fields = config.get("filterset_fields", [])
        search_fields = config.get("search_fields", [])
        ordering_fields = config.get("ordering_fields", [])

        def get_permissions(self):
            if permissions:
                return [p() for p in permissions]

            return [IsAuthenticated()]

        def list(self, request, *args, **kwargs):
            serializer = serializer_class(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            filters = serializer.validated_data

            qs = serializer_class.get_queryset(filters)

            # 3️⃣ Paginate the QuerySet
            paginator_class = api_settings.DEFAULT_PAGINATION_CLASS
            if paginator_class is not None:
                paginator = paginator_class()
                page = paginator.paginate_queryset(qs, request, view=self)
                if page is not None:
                    data = serializer_class.list_data(page)
                    return paginator.get_paginated_response(data)

            # 4️⃣ Fallback (no pagination)
            data = serializer_class.list_data(qs)
            return Response(data)

    DerivedViewSet.__name__ = f"{name.capitalize()}DerivedViewSet"
    return DerivedViewSet
