from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)

geometric_tags = [
    'diamond jubilee',
    'lattice lane',
    'rockport marble'
]

def get_special(product: Resilient, item):
    att_list = item.get('attributeList', None)

    dims = att_list[0].split('x')
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])
    product.finish = att_list[1].lower()
    product.material_type = 'vinyl composite tile'
    return product

def get_special_detail(product: Resilient, data: dict):
    look = data.get('Look', None)
    if look and 'arquet' in look:
        product.look = 'wood'
    else:
        print(look)
        look = 'stone'
        if 'oak' in product.manufacturer_style.lower():
            look = 'wood'
        for tag in geometric_tags:
            if tag in product.manufacturer_style.lower():
                look = 'geometric'
        product.look = look
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
#     look = 'stone'
#     if 'oak' in default_product.manufacturer_style.lower():
#         look = 'wood'
#     for tag in geometric_tags:
#         if tag in default_product.manufacturer_style.lower():
#             look = 'geometric'
#     product.look = look
#     product.save()
