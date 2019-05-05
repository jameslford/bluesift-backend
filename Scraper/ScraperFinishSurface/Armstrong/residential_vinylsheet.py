from BSscraper.utils import clean_value
from ScraperFinishSurface.models import ScraperFinishSurface

thk_dic = {
    'Memories': '.065',
    'StrataMax Best': '.085',
    'StrataMax Better': '.070',
    'StrataMax Good': '.065',
    'CushionStep Good': '.080',
    'Duality Premium': '.080',
    'CushionStep Better': '.100',
}

textile_tags = [
    'linen',
    'kyoto'
]

geometric_tags = [
    'blackwell',
    'philmont'
]

wood_tags = [
    'oak',
    'asian plank',
    'timbers',
    'hickory',
    'farmdale',
    'insbruck',
    'maple',
    'new forest',
    'woodbine',
    'woodcrest'
]

natural_tag = 'framingham'

def get_special(product, item):
    # look = 'stone'
    # if natural_tag in product.manufacturer_style:
    #     look = 'natural pattern'
    # for tag in wood_tags:
    #     if tag in product.manufacturer_style:
    #         look = 'wood'
    # for tag in geometric_tags:
    #     if tag in product.manufacturer_style:
    #         look = 'geometric'
    # for tag in textile_tags:
    #     if tag in product.manufacturer_style:
    #         look = 'textile'
    # product.look = look

    att_list = item.get('attributeList', None)

    gloss = [k for k in att_list if 'Gloss' in k]
    product.finish = gloss[0].lower()
    widths = [clean_value(k) for k in att_list if 'ft.' in k]
    width = '-'.join(widths)
    product.width = width
    product.material = 'vinyl sheet'
    return product

def get_special_detail(product: ScraperFinishSurface, data: dict):
    product.look = data.get('Look', None)
    product.surface_coating = data.get('Wear Layer Type', None)
    return product
