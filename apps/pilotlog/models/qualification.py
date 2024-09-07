from .base_model import BaseModel


class Qualification(BaseModel):

    def __str__(self):
        return f"Qualification {self.guid}"
