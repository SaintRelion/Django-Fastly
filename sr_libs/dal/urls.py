from rest_framework.routers import DefaultRouter
from django.urls import path, include


from .registry import RESOURCE_REGISTRY, DERIVED_RESOURCE_REGISTRY
from .viewset import create_resource_viewset, create_derived_viewset

router = DefaultRouter()

# register standard resources
for name, config in RESOURCE_REGISTRY.items():
    viewset = create_resource_viewset(name, config)
    router.register(config["endpoint"], viewset, basename=name)

# register derived endpoints
derived_patterns = []

for name, config in DERIVED_RESOURCE_REGISTRY.items():
    viewset = create_derived_viewset(name, config)
    # ensure endpoint has trailing slash just like standard resources
    endpoint = config["endpoint"]
    if not endpoint.endswith("/"):
        endpoint += "/"
    derived_patterns.append(path(endpoint, viewset.as_view({"get": "list"})))

urlpatterns = [
    path("", include(router.urls)),
    *derived_patterns,
]
