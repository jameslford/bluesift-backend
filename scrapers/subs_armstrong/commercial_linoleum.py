from Scraper.models import ScraperFinishSurface
from utils.measurements import clean_value

natural_tags = [
    'linorette',
    'marmorette',
    'rythmics'
]


def get_special(product: ScraperFinishSurface, item):
    att_list = item.get('attributeList', None)
    collection = att_list[0].lower()
    product.manufacturer_collection = collection
    product.commercial = True
    product.material = 'resilient'
    product.sub_material = 'linoleum'

    size_line = att_list[1]
    size_split = size_line.split('<br/>')
    if len(size_split) > 1:
        sizes = [s.split('x') for s in size_split]
        print(sizes)
        widths = set([clean_value(x[0]) for x in sizes])
        lengths = set([clean_value(x[1]) for x in sizes])
        thicknessses = set([clean_value(x[2]) for x in sizes])
        product.width = '-'.join(widths)
        product.length = '-'.join(lengths)
        product.thickness = '-'.join(thicknessses)
    else:
        width, length, thickness = size_line.split('x')
        product.width = clean_value(width)
        product.length = clean_value(length)
        product.thickness = clean_value(thickness)
    return product


def get_special_detail(product: ScraperFinishSurface, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.lrv = empty_dict.get('Light Reflectance', None)
    product.install_type = empty_dict.get('Installation Method', None)
    return product


def clean(product: ScraperFinishSurface):
    default_product: ScraperFinishSurface = ScraperFinishSurface.objects.using('scraper_default').get(pk=product.pk)
    if default_product.width:
        width = default_product.width
        width_split = width.split('-')
        if len(width_split) > 1:
            width = width_split[0]
        product.width = width.replace('in.', '').strip()
    if default_product.thickness:
        product.thickness = default_product.thickness.replace('in.', '').strip()
    look = 'solid color'
    if 'colorette' in default_product.manufacturer_collection.lower():
        look = 'solid color'
    if 'granette' in default_product.manufacturer_collection.lower():
        look = 'shaded / specked'
    for tag in natural_tags:
        if tag in default_product.manufacturer_collection.lower():
            look = 'natural pattern'
    product.look = look
    product.save()
