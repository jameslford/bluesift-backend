from SpecializedProducts.models import TileAndStone
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)

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


def get_special(product: TileAndStone, item):
    att_list = item.get('attributeList', None)
    dims = att_list[0].split('x')
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])
    product.finish = att_list[1].lower()
    product.install_type = att_list[2]
    product.material_type = 'engineered'
    look = 'stone'
    for tag in wood_tags:
        if tag in product.manufacturer_style.lower():
            look = 'wood'
    if natural_tag in product.manufacturer_style.lower():
        look = 'natural pattern'
    if solid_tag in product.manufacturer_style.lower():
        look = 'solid color'
    if geometric_tag in product.manufacturer_style.lower():
        look = 'geometric pattern'
    product.look = look
    return product


def get_special_detail(product: TileAndStone, data: dict):
    product.surface_coating = data.get('Wear Layer Type', None)
    return product


# def clean(product: TileAndStone):
#     product: TileAndStone = TileAndStone.objects.using('scraper_default').get(pk=product.pk)
#     product.length = product.length.replace('in.', '').strip() if product.length else None
#     product.width = product.width.replace('in.', '').strip() if product.width else None
#     product.thickness = product.thickness.replace('in.', '').strip() if product.thickness else None
#     product.sub_material = 'engineered tile'
#     look = 'stone'
#     for tag in wood_tags:
#         if tag in product.manufacturer_style.lower():
#             look = 'wood'
#     if natural_tag in product.manufacturer_style.lower():
#         look = 'natural pattern'
#     if solid_tag in product.manufacturer_style.lower():
#         look = 'solid color'
#     if geometric_tag in product.manufacturer_style.lower():
#         look = 'geometric pattern'
#     product.look = look
#     product.save()
