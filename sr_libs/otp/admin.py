from django.contrib import admin
from .models import OTP


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "code",
        "type",
        "verified",
        "attempt_count",
        "expires_at",
        "is_expired",
        "created_at",
    )
    list_filter = ("type", "verified", "expires_at")
    search_fields = ("user__username", "code")
    readonly_fields = ("created_at",)

    def is_expired(self, obj):
        return obj.is_expired()

    is_expired.boolean = True
    is_expired.admin_order_field = "expires_at"
