from .dynamic_model import DynamicModel


class Flight(DynamicModel):
    class Meta:
        db_table = 'flight'


