"""returns float measurements and labels on product details"""
import operator
import decimal
import webcolors
from PIL import Image as pimage
from django.contrib.postgres.fields import DecimalRangeField
from django.db import models
from Products.models import Product

class ProductSubClass(Product):
    """returns float measurements and labels on product details"""
    name_fields = []
    admin_fields = []

    class Meta:
        abstract = True

    def grouped_fields(self):
        """returns attribute groups in product detail on front end"""
        return {}

    def geometries(self):
        """returns float measurements and labels on product details"""
        return {}

    def get_width(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_height(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_depth(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_texture_map(self):
        """returns float measurements and labels on product details"""
        return None

    def get_geometry_model(self):
        return None

    def presentation_geometries(self):
        """returns float measurements and labels on product details"""
        # from .serializers import SubproductGeometryPresentationSerializer
        # return SubproductGeometryPresentationSerializer(self).data
        pass

    @classmethod
    def validate_sub(cls, sub: str):
        """returns float measurements and labels on product details"""
        return bool(sub.lower() in [klas.__name__.lower() for klas in cls.__subclasses__()])

    @classmethod
    def return_sub(cls, sub: str):
        """returns float measurements and labels on product details"""
        classes = [klas for klas in cls.__subclasses__() if klas.__name__.lower() == sub.lower()]
        if classes:
            return classes[0]
        return None

