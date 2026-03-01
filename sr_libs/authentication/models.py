from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserDevice(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="devices"
    )
    device_id = models.CharField(max_length=255)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    is_trusted = models.BooleanField(default=False)
    last_used = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "device_id")
