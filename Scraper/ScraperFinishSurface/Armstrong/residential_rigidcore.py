from config.scripts.measurements import clean_value
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

stone_tags = [
    'stone',
    'castilian',
    'porto alegre',
    'slate',
    'weather way'
]


def get_special(product, item):
    att_list = item.get('attributeList', None)
    if not att_list:
        return product

    dims = att_list[0].split('x')
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])

    product.finish = att_list[1].lower()
    product.install_type = att_list[2]
    product.material = 'resilient'
    product.sub_material = 'rigid core'
    return product

def get_special_detail(product: ScraperFinishSurface, data: dict):
    product.look = data.get('Look', None)
    product.surface_coating = data.get('Wear Layer Type', None)
    return product
