from .base_model import BaseModel


class Pilot(BaseModel):

    def __str__(self):
        return f"Pilot {self.guid}"
