import serpy
from Products.serializers import SerpyProduct


class SerpyFinishSurfaceMini(serpy.Serializer):
    product = SerpyProduct()
