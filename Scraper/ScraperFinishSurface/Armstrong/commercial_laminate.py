from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from config.scripts.measurements import clean_value


def get_special(product: ScraperFinishSurface, item):
    att_list = item.get('attributeList', None)

    product.manufacturer_collection = att_list[0]
    size = att_list[1]
    width, length, thickness = size.split('x')
    product.width = clean_value(width)
    product.length = clean_value(length)
    product.thickness = clean_value(thickness)

    product.look = 'wood'
    product.material = 'laminate flooring'
    product.commercial = True
    return product

def get_special_detail(product: ScraperFinishSurface, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.lrv = empty_dict.get('Light Reflectance', None)
    product.install_type = empty_dict.get('Installation Method', None)
    return product
