from django.db import models


class FlightQuerySet(models.QuerySet):
    def by_airplane(self, airplane_guid):
        return self.filter(
            airplane__guid=airplane_guid
        ).order_by('airplane_guid')


class FlightManager(models.Manager):
    def get_queryset(self):
        return FlightQuerySet(self.model, using=self._db)

    def flight_by_airplane(self, airplane):
        return self.get_queryset().by_airplane(airplane)


