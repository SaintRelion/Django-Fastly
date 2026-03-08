from django.db import models
from django.contrib.auth import get_user_model

from django.forms.models import model_to_dict
from django.core.serializers.json import DjangoJSONEncoder
import json

from .utils import get_current_user, get_client_ip

User = get_user_model()

class AuditLog(models.Model):
    ACTIONS = [
        ("CREATE","CREATE"),
        ("UPDATE","UPDATE"),
        ("DELETE","DELETE"),
        ("LOGIN","LOGIN"),
        ("LOGOUT","LOGOUT"),
        ("EXECUTE","EXECUTE"),
        ("SEND","SEND"),
    ]

    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    source = models.CharField(
        max_length=50,
        choices=[
            ("user","user"),
            ("anonymous","anonymous"),
            ("system","system"),
            ("middleware","middleware"),
            ("manual","manual"),
        ],
        default="user"
    )
    action = models.CharField(max_length=10, choices=ACTIONS)
    model_name = models.CharField(max_length=100, null=True, blank=True)
    object_id = models.CharField(max_length=100, null=True, blank=True)
    old_data = models.JSONField(null=True, blank=True)
    new_data = models.JSONField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    auth_method = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.action} {self.model_name} ({self.object_id}) by {self.user or self.source}"


class AuditModel(models.Model):
    """Abstract base class to inherit for automatic CRUD logging"""

    class Meta:
        abstract = True

    def _serialize_instance(self, instance):
        """Return a JSON-serializable dict of model fields"""
        if not instance:
            return None
        data = model_to_dict(instance, fields=[f.name for f in instance._meta.fields])
        return json.loads(json.dumps(data, cls=DjangoJSONEncoder))

    def save(self, *args, **kwargs):
        user = get_current_user()
        ip = get_client_ip()
        action = "UPDATE" if self.pk else "CREATE"

        # Serialize old data before saving
        old_instance = self.__class__.objects.filter(pk=self.pk).first() if self.pk else None
        old_data = self._serialize_instance(old_instance)

        super().save(*args, **kwargs)

        # Serialize new data after save
        new_data = self._serialize_instance(self)

        AuditLog.objects.create(
            user=user,
            source="user" if user else "anonymous",
            model_name=self._meta.label,  # app_label.ModelName
            object_id=self.pk,
            action=action,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip,
        )

    def delete(self, *args, **kwargs):
        user = get_current_user()
        ip = get_client_ip()

        old_data = self._serialize_instance(self)

        AuditLog.objects.create(
            user=user,
            source="user" if user else "anonymous",
            model_name=self._meta.label,
            object_id=self.pk,
            action="DELETE",
            old_data=old_data,
            ip_address=ip,
        )

        super().delete(*args, **kwargs)