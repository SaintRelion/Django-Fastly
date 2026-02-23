from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models


class User(AbstractUser):
    extra_info = models.JSONField(default=dict, blank=True)

    # override reverse accessors
    groups = models.ManyToManyField(
        Group,
        related_name="sr_accounts_users",  # unique
        blank=True,
        help_text="The groups this user belongs to.",
        verbose_name="groups",
    )

    user_permissions = models.ManyToManyField(
        Permission,
        related_name="sr_accounts_users_permissions",  # unique
        blank=True,
        help_text="Specific permissions for this user.",
        verbose_name="user permissions",
    )

    def __str__(self):
        return self.username
