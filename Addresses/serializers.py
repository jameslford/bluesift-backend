from rest_framework import serializers
from .models import Address

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = (
            'address_line_1', 
            # 'address_line_2',
            'city',
            # 'country',
            'state',
            'postal_code'
        )