from django.db import models
from django.utils import timezone


class OTP(models.Model):
    TYPE_CHOICES = [
        ("sms", "SMS"),
        ("email", "Email"),
    ]

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="otps"
    )
    code = models.CharField(max_length=6)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default="sms")
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    verified = models.BooleanField(default=False)
    attempt_count = models.PositiveIntegerField(default=0)
    additional_info = models.JSONField(default=dict, blank=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"{self.user.username} - {self.code} ({'verified' if self.verified else 'pending'})"
