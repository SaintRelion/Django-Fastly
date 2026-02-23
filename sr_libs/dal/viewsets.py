from rest_framework import viewsets, status
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from django.db.models import QuerySet

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
                filter_kwargs = {}

                for key, value in self.request.query_params.items():
                    value = value.strip('"')  # remove quotes if frontend sent "Active"
                    try:
                        field = model._meta.get_field(key)
                        if isinstance(field, models.ForeignKey):
                            # convert FK to underlying id field
                            key = f"{key}_id"
                    except FieldDoesNotExist:
                        # skip unknown fields
                        continue

                    # Optional: handle comma-separated lists for __in filtering
                    if "," in value:
                        filter_kwargs[f"{key}__in"] = value.split(",")
                    else:
                        filter_kwargs[key] = value

                if filter_kwargs:
                    qs = qs.filter(**filter_kwargs)

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
                f"{model.__name__}{dal_action.capitalize()}Serializer",
            )

        def destroy(self, request, *args, **kwargs):
            if not operations.get("delete"):
                raise MethodNotAllowed("Delete not allowed")

            return super().destroy(request, *args, **kwargs)

        def perform_destroy(self, instance):
            if operations.get("archive"):
                if not isinstance(instance, ArchiveMixin):
                    raise ValueError(
                        f"{model.__name__} must inherit ArchiveMixin for archive support."
                    )
                instance.is_archived = True
                instance.save()
            else:
                super().perform_destroy(instance)

    DynamicViewSet.__name__ = f"{model.__name__}ViewSet"

    return DynamicViewSet
