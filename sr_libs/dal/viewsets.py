from rest_framework import viewsets
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

    class DynamicViewSet(viewsets.ModelViewSet):
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

            if not operations.get(dal_action):
                raise MethodNotAllowed(f"{dal_action} not allowed")

            fields = operations[dal_action]

            return create_dynamic_serializer(
                model,
                fields,
                f"{name.capitalize()}{dal_action.capitalize()}Serializer",
            )

        def destroy(self, request, *args, **kwargs):
            if not operations.get("delete"):
                raise MethodNotAllowed("Delete not allowed")

            return super().destroy(request, *args, **kwargs)

        def perform_create(self, serializer):
            instance = serializer.save()
            data = self.request.data

            # Handle special models on creation
            if hasattr(instance, "update_with_extra_info"):
                instance.update_with_extra_info(data)

        def perform_update(self, serializer):
            instance = serializer.instance

            if hasattr(instance, "update_with_extra_info"):
                instance.update_with_extra_info(self.request.data)

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

    DynamicViewSet.__name__ = f"{name.capitalize()}ViewSet"

    return DynamicViewSet
