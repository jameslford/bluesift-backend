import decimal
from psycopg2.extras import NumericRange
from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special, get_special_detail)

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

natural_tag = ['framingham']

look_dict = {
    'textile': textile_tags,
    'geometric_pattern': geometric_tags,
    'wood': wood_tags,
    'natural_pattern': natural_tag,
}

def get_special(product: Resilient, item):
    att_list = item.get('attributeList', None)

    gloss = [k for k in att_list if 'Gloss' in k]
    product.finish = gloss[0].lower()
    widths = [clean_value(k) for k in att_list if 'ft.' in k]
    product.width = NumericRange(min(widths), max(widths))
    product.material_type = 'vinyl sheet'
    product.look = assign_look(product)
    product.shape = 'continuous'
    thickness = thk_dic.get(product.manufacturer_collection, None)
    product.thickness = decimal.Decimal(thickness)
    return product


def get_special_detail(product: Resilient, data: dict):
    # product.look = data.get('Look', None)
    product.surface_coating = data.get('Wear Layer Type', None)
    return product


def assign_look(product: Resilient):
    for look, tag_list in look_dict.items():
        for tag in tag_list:
            if tag in product.manufacturer_style.lower():
                return look
    return 'stone'

# def clean(product: Resilient):
#     default_product: Resilient = Resilient.objects.get(pk=product.pk)
#     product.length = '0-120'
#     product.width = '0-144'
#     product.thickness = thk_dic.get(default_product.manufacturer_collection, None)
#     product.look = assign_look(default_product)
#     product.save()


