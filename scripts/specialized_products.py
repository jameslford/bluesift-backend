from typing import List
# from SpecializedProducts.models import ProductSubClass
from Products.models import Product

def convert_geometries():
    # products: List[ProductSubClass] = ProductSubClass.objects.all()
    products = Product.subclasses.select_related('manufacturer').all().select_subclasses()
    for product in products:
        if not product.derived_gbl:
            product.convert_geometries()
