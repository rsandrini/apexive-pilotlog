from .base_model import BaseModel


class MyQuery(BaseModel):

    def __str__(self):
        return f"myQuery {self.guid}"
