from config.scripts.measurements import clean_value
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

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

def get_special(product, item):
    att_list = item.get('attributeList', None)

    gloss = [k for k in att_list if 'Gloss' in k]
    product.finish = gloss[0].lower()
    widths = [clean_value(k) for k in att_list if 'ft.' in k]
    width = '-'.join(widths)
    product.width = width
    product.material = 'resilient'
    product.sub_material = 'vinyl sheet'
    return product

def get_special_detail(product: ScraperFinishSurface, data: dict):
    product.look = data.get('Look', None)
    product.surface_coating = data.get('Wear Layer Type', None)
    return product


def clean(product: ScraperFinishSurface):
    default_product: ScraperFinishSurface = ScraperFinishSurface.objects.get(pk=product.pk)
    product.length = '0-120'
    product.width = '144'
    product.thickness = thk_dic.get(default_product.manufacturer_collection, None)
    product.look = assign_look(default_product)
    product.shape = 'continuous'
    product.save()


def assign_look(default_product: ScraperFinishSurface):
    for look in look_dict:
        tag_list = look_dict[look]
        for tag in tag_list:
            if tag in default_product.manufacturer_style.lower():
                return look
    return 'stone'
