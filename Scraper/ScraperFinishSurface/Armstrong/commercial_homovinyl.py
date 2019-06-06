from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from config.scripts.measurements import clean_value


def get_special(product: ScraperFinishSurface, item):
    att_list = item.get('attributeList', None)
    product.look = 'shaded / specked'
    product.material = 'resilient'
    product.sub_material = 'sheet vinyl'
    product.commercial = True
    product.manufacturer_collection = att_list[0]
    width, length, thickness = att_list[1].split('x')
    product.width = clean_value(width)
    product.length = clean_value(length)
    product.thickness = clean_value(thickness)
    return product


def get_special_detail(product: ScraperFinishSurface, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.lrv = empty_dict.get('Light Reflectance', None)
    product.install_type = empty_dict.get('Installation Method', None)
    return product
