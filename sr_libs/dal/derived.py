from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .registry import DERIVED_RESOURCE_REGISTRY


def create_derived_view(name, config):
    resolver = config["resolver"]
    operations = config["operations"]

    class DerivedView(APIView):
        def get(self, request):
            if not operations.get("list"):
                return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

            data = resolver(filters=request.query_params)
            return Response(data)

    DerivedView.__name__ = f"{name.capitalize()}DerivedView"
    return DerivedView


def register_derived_resource(
    *,
    name: str,
    endpoint: str,
    resolver,
    operations: dict,
):
    DERIVED_RESOURCE_REGISTRY[name] = {
        "endpoint": endpoint,
        "resolver": resolver,
        "operations": operations,
    }
