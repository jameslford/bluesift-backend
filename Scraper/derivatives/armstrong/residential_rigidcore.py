from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)

stone_tags = [
    'stone',
    'castilian',
    'porto alegre',
    'slate',
    'weather way'
]


def get_special(product: Resilient, item):
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
    product.material_type = 'rigid core'
    look = 'wood'
    for tag in stone_tags:
        if tag in product.manufacturer_style.lower():
            look = 'stone'
    product.look = look
    return product


def get_special_detail(product: Resilient, data: dict):
    product.surface_coating = data.get('Wear Layer Type', None)
    return product

# def clean(product: Resilient):
#     default_product: Resilient = Resilient.objects.get(pk=product.pk)
#     if default_product.length:
#         product.length = default_product.length.replace('in.', '').strip()
#     if default_product.width:
#         product.width = default_product.width.replace('in.', '').strip()
#     if default_product.thickness:
#         product.thickness = default_product.thickness.replace('in.', '').strip()
#     look = 'wood'
#     for tag in stone_tags:
#         if tag in product.manufacturer_style.lower():
#             look = 'stone'
#     product.look = look
#     product.save()
