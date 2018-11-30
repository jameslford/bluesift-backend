from rest_framework import serializers
from .models import Address, Coordinate

class CoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = (
            'lat',
            'lng'
        )

class AddressSerializer(serializers.ModelSerializer):
    coordinates = CoordinateSerializer()
    class Meta:
        model = Address
        fields = (
            'address_line_1', 
            'city',
            'country',
            'state',
            'postal_code',
            'coordinates',
            'address_string'
        )