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
