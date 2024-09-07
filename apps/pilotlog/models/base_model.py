from django.db import models


class BaseModel(models.Model):
    guid = models.UUIDField(editable=False, primary_key=True)
    user_id = models.IntegerField()
    platform = models.IntegerField()
    _modified = models.BigIntegerField()
    meta = models.JSONField()

    class Meta:
        abstract = True
