from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape


def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)

textile_tags = ['linen', 'tweed']
wood_tags = ['oak', 'maple', 'cherry', 'bamboo', 'walnut', 'timber', 'mallorca', 'echo']
stone_tags = ['stone', 'fossil', 'slate', 'travertini']
metal_tags = ['steel']

def get_special(product: Resilient, item):
    product.material_type = 'sheet vinyl'
    product.commercial = True
    att_list = item.get('attributeList', None)
    collection = att_list[0]
    width, length, thickness = att_list[1].split('x')
    print(width, length, thickness)
    product.manufacturer_collection = collection
    product.width = clean_value(width)
    product.length = clean_value(length)
    product.thickness = clean_value(thickness)
    return product


def get_special_detail(product: Resilient, empty_dict: dict):
    gloss = empty_dict.get('gloss', None)
    lrv = empty_dict.get('Light Reflectance', None)
    install_type = empty_dict.get('Installation Method', None)
    product.finish = gloss
    product.install_type = install_type
    product.lrv = lrv
    return product


def clean(product: Resilient):
    default_product: Resilient = Resilient.objects.get(pk=product.pk)
    look = 'shaded / specked'
    if 'ambigu' in default_product.manufacturer_collection.lower():
        look = 'textile'
    elif 'stonerun' in default_product.manufacturer_collection.lower():
        look = 'stone'
    elif 'timber' in default_product.manufacturer_collection.lower():
        look = 'wood'
    else:
        for tag in textile_tags:
            if tag in default_product.manufacturer_style.lower():
                look = 'textile'
        for tag in wood_tags:
            if tag in default_product.manufacturer_style.lower():
                look = 'wood'
        for tag in stone_tags:
            if tag in default_product.manufacturer_style.lower():
                look = 'stone'
        if 'steel' in default_product.manufacturer_style.lower():
            look = 'metal'
    product.look = look
    product.shape = 'continuous'
    if default_product.width:
        width = default_product.width.replace('ft.', '').strip()
        width = round((float(width) * 12), 2)
        product.width = '0-' + str(width)
    if default_product.length:
        length = default_product.length.replace('up to', '')
        length = length.replace('ft.', '').strip()
        length = round((float(length) * 12), 2)
        product.length = '0-' + str(length)
    if default_product.thickness:
        product.thickness = default_product.thickness.replace('in.', '').strip()
    product.save()
