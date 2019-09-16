from rest_framework import serializers
from .models import ProductViewRecord


class ProductViewRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = ProductViewRecord
        fields = '__all__'