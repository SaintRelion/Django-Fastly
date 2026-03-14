from django.contrib import admin
from django.db import models

from .registry import RESOURCE_REGISTRY

# Dynamically register all resources from the DAL
for resource_name, resource_info in RESOURCE_REGISTRY.items():
    model = resource_info["model"]

    # Optional: create a default ModelAdmin
    class DynamicAdmin(admin.ModelAdmin):
        list_display = [field.name for field in model._meta.fields]
        search_fields = [
            field.name
            for field in model._meta.fields
            if isinstance(field, (models.CharField, models.TextField))
        ]

    admin.site.register(model, DynamicAdmin)
