from config.scripts.measurements import clean_value
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

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
    att_list = item.get('attributeList', None)
    dims = att_list[0].split('x')
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])
    product.finish = att_list[1].lower()
    product.install_type = att_list[2]
    product.material = 'stone & glass'
    product.sub_material = 'engineered tile'
    return product


def get_special_detail(product: ScraperFinishSurface, data: dict):
    product.surface_coating = data.get('Wear Layer Type', None)
    product.look = data.get('Look', None)
    return product


def clean(product: ScraperFinishSurface):
    default_product: ScraperFinishSurface = ScraperFinishSurface.objects.using('scraper_default').get(pk=product.pk)
    product.length = default_product.length.replace('in.', '').strip() if default_product.length else None
    product.width = default_product.width.replace('in.', '').strip() if default_product.width else None
    product.thickness = default_product.thickness.replace('in.', '').strip() if default_product.thickness else None
    product.sub_material = 'engineered tile'
    look = 'stone'
    for tag in wood_tags:
        if tag in default_product.manufacturer_style.lower():
            look = 'wood'
    if natural_tag in default_product.manufacturer_style.lower():
        look = 'natural pattern'
    if solid_tag in default_product.manufacturer_style.lower():
        look = 'solid color'
    if geometric_tag in default_product.manufacturer_style.lower():
        look = 'geometric pattern'
    product.look = look
    product.save()
