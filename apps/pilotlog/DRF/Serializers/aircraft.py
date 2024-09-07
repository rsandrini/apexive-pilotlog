from rest_framework import serializers
from pilotlog.models.aircraft import Aircraft


class AircraftListSerializer(serializers.ModelSerializer):
    reference = serializers.SerializerMethodField()
    make = serializers.SerializerMethodField()

    class Meta:
        model = Aircraft
        fields = ('guid', 'reference', 'make')

    def get_reference(self, obj):
        # Replace 'meta' with the actual attribute name if it's a JSONField
        return obj.meta.get('Reference', None) if obj.meta else None

    def get_make(self, obj):
        # Replace 'meta' with the actual attribute name if it's a JSONField
        return obj.meta.get('Make', None) if obj.meta else None


class AircraftDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Aircraft
        fields = '__all__'  # All fields for detailed view