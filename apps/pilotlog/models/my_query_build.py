from .base_model import BaseModel


class MyQueryBuild(BaseModel):

    def __str__(self):
        return f"myQueryBuild {self.guid}"
