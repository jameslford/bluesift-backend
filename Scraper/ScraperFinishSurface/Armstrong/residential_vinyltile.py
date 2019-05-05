from BSscraper.utils import clean_value
from ScraperFinishSurface.models import ScraperFinishSurface

geometric_tags = [
    'diamond jubilee',
    'lattice lane',
    'rockport marble'
]

def get_special(product, item):
    att_list = item.get('attributeList', None)

    dims = att_list[0].split('x')
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])
    product.finish = att_list[1].lower()
    # look = 'stone'
    # if 'oak' in product.manufacturer_style:
    #     look = 'wood'
    # for tag in geometric_tags:
    #     if tag in product.manufacturer_style:
    #         look = 'geometric'
    # product.look = look
    product.material = 'vinyl tile'
    return product

def get_special_detail(product: ScraperFinishSurface, data: dict):
    look = data.get('Look', None)
    if look and 'arquet' in look:
        product.look = 'wood'
    else:
        product.look = look
    product.surface_coating = data.get('Wear Layer Type', None)
    return product
