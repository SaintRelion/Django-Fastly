from rest_framework.routers import DefaultRouter
from django.urls import path, include


from .registry import RESOURCE_REGISTRY, DERIVED_RESOURCE_REGISTRY
from .viewsets import create_resource_viewset
from .derived import create_derived_view

router = DefaultRouter()

# register standard resources
for name, config in RESOURCE_REGISTRY.items():
    viewset = create_resource_viewset(name, config)
    router.register(config["endpoint"], viewset, basename=name)

# register derived endpoints
derived_patterns = []

for name, config in DERIVED_RESOURCE_REGISTRY.items():
    view = create_derived_view(name, config)
    derived_patterns.append(path(config["endpoint"], view.as_view()))

urlpatterns = [
    path("", include(router.urls)),
    *derived_patterns,
]
