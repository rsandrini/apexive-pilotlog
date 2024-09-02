from django.contrib import admin
from .models.aircraft import Aircraft
from .models.flight import Flight

class AircraftAdmin(admin.ModelAdmin):
    model = Aircraft

class FlightAdmin(admin.ModelAdmin):
    model = Flight


admin.site.register(Aircraft, AircraftAdmin)
admin.site.register(Flight, FlightAdmin)