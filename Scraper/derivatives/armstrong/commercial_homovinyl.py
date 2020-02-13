import decimal
from psycopg2.extras import NumericRange
from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape


def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)


def get_special(product: Resilient, item):
    att_list = item.get('attributeList', None)
    product.look = 'shaded / specked'
    product.material_type = 'sheet vinyl'
    product.commercial = True
    product.manufacturer_collection = att_list[0]
    width, length, thickness = att_list[1].split('x')
    product.width = NumericRange(clean_value(width))
    product.length = NumericRange(clean_value(length))
    product.thickness = decimal.Decimal(clean_value(thickness))
    return product


def get_special_detail(product: Resilient, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.lrv = empty_dict.get('Light Reflectance', None)
    product.install_type = empty_dict.get('Installation Method', None)
    product.shape = 'continuous'
    return product


# def clean(product: Resilient):
#     default_product: Resilient = Resilient.objects.using('scraper_default').get(pk=product.pk)
#     if default_product.width:
#         width = default_product.width.replace('ft.', '').strip()
#         width = round((float(width) * 12), 2)
#         product.width = '0-' + str(width)
#     if default_product.length:
#         length = default_product.length.replace('up to', '')
#         length = length.replace('ft.', '').strip()
#         length = round((float(length) * 12), 2)
#         product.length = '0-' + str(length)
#     if default_product.thickness:
#         product.thickness = default_product.thickness.replace('in.', '').strip()
#     product.save()
