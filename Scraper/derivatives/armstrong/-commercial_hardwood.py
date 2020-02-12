from SpecializedProducts.models import Hardwood
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)


def get_special(product: Hardwood, item):
    product.material = 'engineered hardwood'
    product.commercial = True
    product.look = 'wood'
    att_list = item.get('attributeList', None)
    product.manufacturer_collection = att_list[0]
    dims = att_list[1]
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])
    return product


def get_special_detail(product: Hardwood, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.lrv = empty_dict.get('Light Reflectance', None)
    product.install_type = empty_dict.get('Installation Method', None)
    product.sub_material = empty_dict.get('Wood Species', None)
    product.sqft_per_carton = empty_dict.get('Coverage Per Carton', None)
    edge_end = empty_dict.get('Edge Detail', None)
    edge = None
    end = None
    if edge_end:
        split = edge_end.split('/')
        if len(split) > 1:
            edge, end = split
        else:
            edge = edge_end
            end = edge_end
    product.edge = edge
    product.end = end
    return product
