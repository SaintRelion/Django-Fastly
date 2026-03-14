from django.contrib import admin
from .models import ScheduledTask


# --- ScheduledTask Admin ---
@admin.register(ScheduledTask)
class ScheduledTaskAdmin(admin.ModelAdmin):
    list_display = (
        "model",
        "instance_id",
        "rule_name",
        "scheduled_at",
        "repeat_every",
        "status",
        "created_at",
    )
    list_filter = ("status", "model", "scheduled_at")
    search_fields = ("model", "rule_name", "instance_id")
    readonly_fields = ("created_at",)
    ordering = ("-scheduled_at",)

    def has_add_permission(self, request, obj=None):
        # Typically ScheduledTask should only be created via signals/tasks
        return False

    def has_delete_permission(self, request, obj=None):
        # Optionally allow admin to delete tasks manually
        return True
