from django.db import models


class ArchiveMixin(models.Model):
    is_archived = models.BooleanField(default=False)

    class Meta:
        abstract = True
