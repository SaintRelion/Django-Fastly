from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.db import models

from .registry import RESOURCE_REGISTRY

# Register your custom User separately
admin.site.register(get_user_model(), UserAdmin)

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
