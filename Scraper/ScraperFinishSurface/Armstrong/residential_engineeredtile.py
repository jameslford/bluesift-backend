from BSscraper.utils import clean_value
from ScraperFinishSurface.models import ScraperFinishSurface

wood_tags = [
    'historic district',
    'ideal candidate',
    'grain directions',
    'miles of trail',
    'rustic isolation',
    'time for tea'
]

natural_tag = 'urban gallery'
geometric_tag = 'regency essence'
solid_tag = 'solid colors'

def get_special(product, item):
    # look = 'stone'
    # for tag in wood_tags:
    #     if tag in product.manufacturer_style:
    #         look = 'wood'
    # if natural_tag in product.manufacturer_style:
    #     look = 'natural pattern'
    # if solid_tag in product.manufacturer_style:
    #     look = 'solid color'
    # if geometric_tag in product.manufacturer_style:
    #     look = 'geometric pattern'
    # product.look = look

    att_list = item.get('attributeList', None)
    dims = att_list[0].split('x')
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])
    product.finish = att_list[1].lower()
    product.install_type = att_list[2]
    product.material = 'stone & glass'
    product.submaterial = 'engineered tile'
    return product

def get_special_detail(product: ScraperFinishSurface, data: dict):
    product.surface_coating = data.get('Wear Layer Type', None)
    product.look = data.get('Look', None)
    return product