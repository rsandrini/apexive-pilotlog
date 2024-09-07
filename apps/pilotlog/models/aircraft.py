from django.db import models
from .base_model import BaseModel


class Aircraft(BaseModel):

    def __str__(self):
        return self.meta.get('Make', 'Unknown Aircraft')
