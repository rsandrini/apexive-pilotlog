from django.db import models
from .base_model import BaseModel
from .aircraft import Aircraft
from ..managers.flight import FlightManager


class Flight(BaseModel):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE,
                                 related_name='flights')

    objects = FlightManager()
    def __str__(self):
        return f"Flight {self.guid} on {self.meta.get('DateUTC', 'Unknown Date')}"
