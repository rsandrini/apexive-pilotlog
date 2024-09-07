from django.db import models


class AircraftQuerySet(models.QuerySet):
    def active(self):
        return self.filter(meta__Active=True)

    def by_make(self, make):
        return self.filter(meta__Make=make)

    def high_performance_complex(self):
        return self.filter(
            meta__HighPerf=True,
            meta__Complex=True,
            meta__Active=True
        ).order_by('-meta__Make')


class AircraftManager(models.Manager):
    def get_queryset(self):
        return AircraftQuerySet(self.model, using=self._db)

    def active_aircraft(self):
        return self.get_queryset().active()

    def aircraft_by_make(self, make):
        return self.get_queryset().by_make(make)

    def high_performance_complex_aircraft(self):
        return self.get_queryset().high_performance_complex()