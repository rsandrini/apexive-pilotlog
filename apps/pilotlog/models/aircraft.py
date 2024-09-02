from .dynamic_model import DynamicModel


class Aircraft(DynamicModel):
    class Meta:
        db_table = 'aircraft'
