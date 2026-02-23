from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    extra_info = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return self.username
