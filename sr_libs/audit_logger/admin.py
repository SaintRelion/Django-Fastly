from django.contrib import admin
from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):

    list_display = (
        "action",
        "category",
        "object_id",
        "user",
        "source",
        "ip_address",
        "created_at",
    )

    list_filter = (
        "action",
        "source",
        "category",
        "created_at",
    )

    search_fields = (
        "category",
        "object_id",
        "user__username",
        "ip_address",
    )

    readonly_fields = [f.name for f in AuditLog._meta.fields]

    ordering = ("-created_at",)

    date_hierarchy = "created_at"
