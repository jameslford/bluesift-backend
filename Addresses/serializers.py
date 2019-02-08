from rest_framework import serializers
from .models import Address, Coordinate, Zipcode


class CoordinateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coordinate
        fields = (
            'lat',
            'lng'
        )


class ZipcodeSerializer(serializers.ModelSerializer):
    # centroid = CoordinateSerializer()

    class Meta:
        model = Zipcode
        fields = (
            'id',
            'code',
            # 'centroid'
            )


class AddressUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address
        fields = (
            'address_line_1',
            'city',
            'country',
            'state',
            'postal_code',
        )


class AddressSerializer(serializers.ModelSerializer):
    coordinates = CoordinateSerializer()
    postal_code = ZipcodeSerializer()


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
