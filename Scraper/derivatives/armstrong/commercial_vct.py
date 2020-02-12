import decimal
from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from psycopg2.extras import NumericRange
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)


def get_special(product: Resilient, item):
    att_list = item.get('attributeList', None)
    product.commercial = True
    product.material_type = 'vinyl composite tile'
    collection = att_list[0].lower()
    look = 'shaded / specked'
    if 'feature' in collection:
        look = 'solid color'
    if 'stream' in collection:
        look = 'natural pattern'
    product.look = look
    product.manufacturer_collection = collection
    size_line = att_list[1]
    size_split = size_line.split('<br/>')
    if len(size_split) > 1:
        sizes = [s.split('x') for s in size_split]
        widths = [clean_value(x[0]) for x in sizes]
        lengths = [clean_value(x[1]) for x in sizes]
        thicknesses = [clean_value(x[2]) for x in sizes]
        width = NumericRange(min(widths), max(widths))
        length = NumericRange(min(lengths), max(lengths))
        product.width = width
        product.length = length
        product.thickness = decimal.Decimal(thicknesses[-1])
    else:
        width, length, thickness = size_line.split('x')
        width = clean_value(width)
        length = clean_value(length)
        thickness = clean_value(thickness)
        print(width, length, thickness)
        product.width = NumericRange(width)
        product.length = NumericRange(length)
        product.thickness = decimal.Decimal(thickness)
    return product


def get_special_detail(product: Resilient, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.lrv = empty_dict.get('Light Reflectance', None)
    product.install_type = empty_dict.get('Installation Method', None)
    return product
