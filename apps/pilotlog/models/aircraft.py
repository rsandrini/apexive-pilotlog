from django.db import models
from .base_model import BaseModel
from ..managers.aircraft import AircraftManager


class Aircraft(BaseModel):
    objects = AircraftManager()
    def __str__(self):
        return self.meta.get('Make', 'Unknown Aircraft')
