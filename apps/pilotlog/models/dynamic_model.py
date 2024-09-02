from django.db import models
from uuid import uuid4


class DynamicModel(models.Model):
    guid = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    user_id = models.IntegerField()
    platform = models.IntegerField()
    _modified = models.BigIntegerField()
    meta = models.JSONField()

    def __str__(self):
        return f"{self.__class__.__name__} {self.guid}"
