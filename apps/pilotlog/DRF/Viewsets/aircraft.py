from rest_framework import viewsets
from pilotlog.models.aircraft import Aircraft
from ..Serializers.aircraft import AircraftListSerializer, AircraftDetailSerializer
from rest_framework.pagination import PageNumberPagination


class AircraftPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100


class AircraftViewSet(viewsets.ModelViewSet):
    queryset = Aircraft.objects.all()
    pagination_class = AircraftPagination

    def get_serializer_class(self):
        if self.action == 'list':
            return AircraftListSerializer
        return AircraftDetailSerializer


