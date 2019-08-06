import serpy
from .models import Product


class TitleField(serpy.Field):

    def to_value(self, value: str):
        return value.lower().title()


class SerpyManufacturer(serpy.Serializer):
    pk = serpy.Field('id')
    label = serpy.Field()


class SerpyProduct(serpy.Serializer):
    pk = serpy.MethodField()
    unit = serpy.Field()
    manufacturer_style = TitleField()
    manu_collection = TitleField()
    manufacturer_sku = serpy.Field()
    name = serpy.Field()
    swatch_image = serpy.MethodField()
    manufacturer = SerpyManufacturer()
    low_price = serpy.MethodField()

    def get_low_price(self, prod_obj):
        if hasattr(prod_obj, 'low_price'):
            return prod_obj.low_price
        return None

    def get_swatch_image(self, prod_obj):
        if prod_obj.swatch_image:
            return prod_obj.swatch_image.url
        return None

    def get_pk(self, prod_obj: Product):
        return str(prod_obj.bb_sku)
