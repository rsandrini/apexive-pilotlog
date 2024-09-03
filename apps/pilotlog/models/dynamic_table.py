from django.db import models
from uuid import uuid4


class DynamicTable(models.Model):
    table = models.CharField(max_length=255)
    guid = models.CharField(max_length=255)
    user_id = models.IntegerField()
    platform = models.IntegerField()
    _modified = models.BigIntegerField()
    meta = models.JSONField()

    def __str__(self):
        return f"{self.table} {self.guid}"

