from django.db import models
from .base_model import BaseModel
from .aircraft import Aircraft


class Flight(BaseModel):
    aircraft = models.ForeignKey(Aircraft, on_delete=models.CASCADE,
                                 related_name='flights')

    def __str__(self):
        return f"Flight {self.guid} on {self.meta.get('DateUTC', 'Unknown Date')}"
