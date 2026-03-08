from django.contrib import admin
from .models import AuditLog

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action","model_name","object_id","user","source","created_at")
    list_filter = ("action","source","model_name")
    search_fields = ("model_name","object_id","user__username")
    readonly_fields = [f.name for f in AuditLog._meta.fields]