from rest_framework.response import Response
from rest_framework import serializers, viewsets
from rest_framework.exceptions import MethodNotAllowed

from .utils import apply_dynamic_filters
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


def create_resource_viewset(name, config):
    model = config["model"]
    operations = config["operations"]

    base_queryset = model.objects.all()

    class ResourceViewSet(viewsets.ModelViewSet):
        queryset = base_queryset
        serializer_class = None  # dynamic

        def get_queryset(self):
            qs = super().get_queryset()
            if operations.get("archive") and hasattr(model, "is_archived"):
                return qs.filter(is_archived=False)

            # dynamic filtering from query params
            if self.action == "list":
                qs = apply_dynamic_filters(qs, model, self.request.query_params)

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
    operations = config["operations"]

    class DerivedViewSet(viewsets.ViewSet):
        def list(self, request, *args, **kwargs):
            if not operations.get("list"):
                raise MethodNotAllowed("list not allowed")

            serializer = serializer_class(data=request.query_params)
            serializer.is_valid(raise_exception=True)
            filters = serializer.validated_data

            data = serializer_class.list_data(filters)
            return Response(data)

    DerivedViewSet.__name__ = f"{name.capitalize()}DerivedViewSet"
    return DerivedViewSet
