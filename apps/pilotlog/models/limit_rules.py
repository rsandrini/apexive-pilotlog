from .base_model import BaseModel


class LimitRules(BaseModel):

    def __str__(self):
        return f"LimitRules {self.guid}"
