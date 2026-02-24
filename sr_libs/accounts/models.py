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

    def update_with_extra_info(self, data: dict):
        """
        Update known columns normally, merge unknown keys into extra_info.
        """
        user_fields = {f.name for f in self._meta.get_fields() if f.concrete}
        extra_updates = {}

        for key, value in data.items():
            if key in user_fields:
                setattr(self, key, value)
            else:
                extra_updates[key] = value

        if extra_updates:
            self.extra_info.update(extra_updates)

        self.save()

    def __str__(self):
        return self.username
