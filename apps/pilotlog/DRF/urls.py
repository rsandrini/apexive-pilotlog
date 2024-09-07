from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .Viewsets.aircraft import AircraftViewSet
from .Viewsets.flight import FlightViewSet


router = DefaultRouter()

router.register(r'aircraft', AircraftViewSet, basename='aircraft')

# Define the urlpatterns with nested routes
urlpatterns = [
    path('', include(router.urls)),
    path('flights/', FlightViewSet.as_view({'get': 'list'}), name='all-flights'),
    path('aircraft/<uuid:aircraft_guid>/flights/', FlightViewSet.as_view({'get': 'list'}), name='aircraft-flights'),
]