import serpy
from typing import Dict
from .models import Product


class TitleField(serpy.Field):

    def to_value(self, value: str):
        return value.lower().title()


class SerpyManufacturer(serpy.Serializer):
    pk = serpy.Field('id')
    label = serpy.Field()


def serialize_product(product: Product) -> Dict[str, any]:
    return {
        'pk': product.pk,
        'unit': product.unit,
        'manufacturer_style': product.manufacturer_style,
        'manu_collection': product.manu_collection,
        'manufacturer_sku': product.manufacturer_sku,
        'name': product.name,
        'swatch_url': product.swatch_image.url if product.swatch_image else None,
        'manufacturer__label': product.manufacturer.label,
        'low_price': getattr(product, 'low_price', None)
        }


def serialize_product_priced(product: Product) -> Dict[str, any]:
    prod_dict = serialize_product(product)
    prod_dict['suppliers'] = [prod.get_priced() for prod in product.priced.all()]
    return prod_dict


# class SerpyProduct(serpy.Serializer):
#     pk = serpy.MethodField()
#     unit = serpy.Field()
#     manufacturer_style = TitleField()
#     manu_collection = TitleField()
#     manufacturer_sku = serpy.Field()
#     name = serpy.Field()
#     swatch_image = serpy.MethodField()
#     manufacturer = SerpyManufacturer()
#     low_price = serpy.MethodField()

#     def get_low_price(self, prod_obj):
#         if hasattr(prod_obj, 'low_price'):
#             return prod_obj.low_price
#         return None

#     def get_swatch_image(self, prod_obj):
#         if prod_obj.swatch_image:
#             return prod_obj.swatch_image.url
#         return None

#     def get_pk(self, prod_obj: Product):
#         return str(prod_obj.bb_sku)
