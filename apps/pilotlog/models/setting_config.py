from django.db import models
from .base_model import BaseModel


class SettingConfig(BaseModel):
    guid = models.CharField(max_length=100)

    def __str__(self):
        return f"SettingConfig {self.guid}"
