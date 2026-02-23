from django.db import models

from django.contrib.auth import get_user_model

User = get_user_model()


class DeviceCredential(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    credential_id = models.BinaryField(unique=True)
    public_key = models.BinaryField()
    sign_count = models.PositiveIntegerField(default=0)

    device_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    last_used_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.device_name}"


class WebAuthnChallenge(models.Model):
    """Stores registration or login challenges for users in Postgres."""

    CHALLENGE_TYPE = [
        ("registration", "Registration"),
        ("authentication", "Authentication"),
    ]

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="webauthn_challenges"
    )
    challenge = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=CHALLENGE_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} challenge"
