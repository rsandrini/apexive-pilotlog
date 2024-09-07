from rest_framework import viewsets
from pilotlog.models.flight import Flight

from ..Serializers.flight import FlightSerializer
from rest_framework.pagination import PageNumberPagination


class FlightPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class FlightViewSet(viewsets.ModelViewSet):
    queryset = Flight.objects.all()
    serializer_class = FlightSerializer
    pagination_class = FlightPagination

    def get_queryset(self):
        # Filter based on the presence of airplane_guid in URL kwargs
        airplane_guid = self.kwargs.get('aircraft_guid')
        if airplane_guid:
            return Flight.objects.filter(aircraft__guid=airplane_guid)
        return Flight.objects.all()