from django.db import models
from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json

from sr_libs.audit_logger.models import AuditLog

from .utils import get_current_user, get_client_ip


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

        ip = get_client_ip()

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

        ip = get_client_ip()

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
