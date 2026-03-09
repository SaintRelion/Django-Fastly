from django.db import models
from django.contrib.auth import get_user_model

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json

User = get_user_model()

# --- ContextVars for async-safe current user/IP ---
import contextvars

current_user_var = contextvars.ContextVar("current_user", default=None)
current_ip_var = contextvars.ContextVar("current_ip", default=None)


def set_current_user(user):
    current_user_var.set(user)


def get_current_user():
    return current_user_var.get()


def set_current_ip(ip):
    current_ip_var.set(ip)


def get_current_ip():
    return current_ip_var.get()


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
        if not user or not getattr(user, "is_authenticated", False):
            user = None

        ip = get_current_ip()

        is_update = bool(self.pk)

        old_instance = None
        if is_update:
            old_instance = self.__class__.objects.filter(pk=self.pk).first()

        super().save(*args, **kwargs)

        if is_update:
            changes = self._get_field_diff(old_instance)
            action = "UPDATE"
        else:
            changes = self._serialize_instance(self)
            action = "CREATE"

        if changes:

            category = getattr(self, "AUDIT_CATEGORY", self.__class__.__name__)

            AuditLog.objects.create(
                user=user,
                source="user" if user else "anonymous",
                category=category,
                action=action,
                object_id=self.pk,
                new_data=changes,
                ip_address=ip,
            )

    def delete(self, *args, **kwargs):

        user = get_current_user()
        if not user or not getattr(user, "is_authenticated", False):
            user = None

        ip = get_current_ip()

        data = self._serialize_instance(self)

        category = getattr(self, "AUDIT_CATEGORY", self.__class__.__name__)

        AuditLog.objects.create(
            user=user,
            source="user" if user else "anonymous",
            category=category,
            action="DELETE",
            object_id=self.pk,
            new_data=data,
            ip_address=ip,
        )

        super().delete(*args, **kwargs)
