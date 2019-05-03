# import serpy
# from Products.serializers import SerpyProduct
# from Products.models import Product
# from .models import FinishSurface
# from rest_framework import serializers


# class SerpyFinishSurfaceMini(serpy.Serializer):
#     product = SerpyProduct()


# class FinishSurfaceMini(serializers.ModelSerializer):
#     product = ProductSerializer()

#     class Meta:
#         model = FinishSurface
#         fields = (
#             'product',
#         )
