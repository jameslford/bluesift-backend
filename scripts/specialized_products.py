from typing import List
from SpecializedProducts.models import ProductSubClass

def convert_geometries():
    products: List[ProductSubClass] = ProductSubClass.objects.all()
    for product in products:
        if not product.derived_gbl:
            product.convert_geometries()
