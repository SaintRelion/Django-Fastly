from django.db import models


class AuditLog(models.Model):
    ACTIONS = [
        ("CREATE", "CREATE"),
        ("UPDATE", "UPDATE"),
        ("DELETE", "DELETE"),
        ("LOGIN", "LOGIN"),
        ("LOGOUT", "LOGOUT"),
        ("EXECUTE", "EXECUTE"),
        ("SEND", "SEND"),
    ]

    user = models.ForeignKey(
        "accounts.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    source = models.CharField(max_length=50, default="user")

    category = models.CharField(max_length=100, null=True, blank=True)

    action = models.CharField(max_length=10, choices=ACTIONS)

    object_id = models.CharField(max_length=100, null=True, blank=True)

    new_data = models.JSONField(null=True, blank=True)

    ip_address = models.GenericIPAddressField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        actor = self.user or self.source
        return f"{self.action} {self.category} ({self.object_id}) by {actor}"
