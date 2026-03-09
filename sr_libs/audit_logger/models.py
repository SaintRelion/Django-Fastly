from django.db import models
from django.contrib.auth import get_user_model

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json

from sr_libs.audit_logger.context import (
    get_current_ip,
    get_current_system,
    get_current_user,
)

User = get_user_model()


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

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

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


class AuditModel(models.Model):
    """Abstract base class to inherit for automatic CRUD logging"""

    IGNORE_FIELDS = {"created_at", "updated_at"}

    class Meta:
        abstract = True

    def _serialize_instance(self, instance):
        """Return a JSON-serializable dict of model fields"""
        if not instance:
            return None
        data = model_to_dict(instance, fields=[f.name for f in instance._meta.fields])
        return json.loads(json.dumps(data, cls=DjangoJSONEncoder))

    def _get_field_diff(self, old_instance):

        if not old_instance:
            return self._serialize_instance(self)

        old_data = self._serialize_instance(old_instance)
        new_data = self._serialize_instance(self)

        diff = {}

        for field, old_value in old_data.items():

            if field in self.IGNORE_FIELDS:
                continue

            new_value = new_data.get(field)

            if old_value != new_value:
                diff[field] = f"{old_value}->{new_value}"

        return diff

    def save(self, *args, **kwargs):
        user = get_current_user()
        system_identity = get_current_system()
        ip = get_current_ip()

        if user and getattr(user, "is_authenticated", False):
            source = "user"
        elif system_identity:
            source = f"system:{system_identity}"
            user = None  # system actions have no human user
        else:
            source = "anonymous"
            user = None

        is_update = bool(self.pk)

        old_instance = None
        old_instance = (
            self.__class__.objects.filter(pk=self.pk).first() if is_update else None
        )

        super().save(*args, **kwargs)

        changes = (
            self._get_field_diff(old_instance)
            if is_update
            else self._serialize_instance(self)
        )
        action = "UPDATE" if is_update else "CREATE"

        if changes:
            AuditLog.objects.create(
                user=user,
                source=source,
                category=getattr(self, "AUDIT_CATEGORY", self.__class__.__name__),
                action=action,
                object_id=self.pk,
                new_data=changes,
                ip_address=ip,
            )

    def delete(self, *args, **kwargs):

        user = get_current_user()
        system_identity = get_current_system()
        ip = get_current_ip()

        if user and getattr(user, "is_authenticated", False):
            source = "user"
        elif system_identity:
            source = f"system:{system_identity}"
            user = None  # system actions have no human user
        else:
            source = "anonymous"
            user = None

        data = self._serialize_instance(self)

        AuditLog.objects.create(
            user=user,
            source=source,
            category=getattr(self, "AUDIT_CATEGORY", self.__class__.__name__),
            action="DELETE",
            object_id=self.pk,
            new_data=data,
            ip_address=ip,
        )

        super().delete(*args, **kwargs)
