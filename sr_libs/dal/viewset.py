from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import serializers, viewsets
from rest_framework.exceptions import MethodNotAllowed
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

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


def create_resource_viewset(name, config):
    model = config["model"]
    operations = config["operations"]

    class ResourceViewSet(viewsets.ModelViewSet):
        queryset = model.objects.all()
        serializer_class = None  # dynamic
        filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
        filterset_fields = config.get("filterset_fields", [])
        search_fields = config.get("search_fields", [])
        ordering_fields = config.get("ordering_fields", [])

        def get_action(self):
            return map_request_to_action(self.request, self.kwargs)

        def get_authenticators(self):
            action = self.get_action()

            auth_config = self.config.get("authenticators", {}).get(action)
            # [] → disable authentication
            if auth_config == []:
                return []

            # default DRF authenticators
            return super().get_authenticators()

        def get_permissions(self):
            action = self.get_action()

            perms = self.config.get("permissions", {}).get(action)
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

            data = serializer_class.list_data(filters)
            return Response(data)

    DerivedViewSet.__name__ = f"{name.capitalize()}DerivedViewSet"
    return DerivedViewSet
