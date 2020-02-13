import decimal
from psycopg2.extras import NumericRange
from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)

stone_tags = [
    'slate',
    'concrete',
    'travertine'
]


def get_special(product: Resilient, item):
    att_list = item.get('attributeList', None)
    product.manufacturer_collection = att_list[0]
    look = 'wood'
    for tag in stone_tags:
        if tag in product.manufacturer_style:
            look = 'stone'
    product.look = look
    print(att_list)
    width, length, thickness = att_list[0].split('x')
    product.width = NumericRange(clean_value(width))
    product.length = NumericRange(clean_value(length))
    product.thickness = decimal.Decimal(clean_value(thickness))
    product.finish = att_list[1]
    product.install_type = att_list[2]
    product.material_type = 'rigid core'
    product.commercial = True
    return product

def get_special_detail(product: Resilient, empty_dict: dict):
    if not product.finish:
        product.finish = empty_dict.get('gloss', None)
    if not product.install_type:
        product.install_type = empty_dict.get('Installation Method', None)
    # product.material_type = empty_dict.get('Wood Species', None)
    product.sqft_per_carton = empty_dict.get('Coverage Per Carton', None)
    edge_end = empty_dict.get('Edge Detail', None)
    end = None
    edge = None
    if edge_end:
        split = edge_end.split('/')
        if len(split) > 1:
            edge, end = split
        else:
            edge = edge_end
            end = edge_end
    product.end = end
    product.edge = edge
    return product
