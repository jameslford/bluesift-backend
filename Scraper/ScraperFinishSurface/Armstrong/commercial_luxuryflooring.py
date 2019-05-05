from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from config.scripts.measurements import clean_value

wood_tags = [
    'argent',
    'alder',
    'amarela',
    'barnside',
    'cerisier',
    'driftwood',
    'factory floor',
    'fruitwood',
    'gold rush',
    'hand crafted',
    'homespun',
    'huntington',
    'la crescenta',
    'los angelimed',
    'maple',
    'mill',
    'oak',
    'patina',
    'rose',
    'tigerwood',
    'trunk',
    'tudor',
    'walnut',
    'yosemite',
]

stone_tags = [
    'delicato',
    'rawcrete',
    'durango',
    'rock',
    'sierra',
    'silk scarf',
    'stone',
    'travertine'
]

natural_tags = [
    'aria ',
    'catalina',
    'jet',
    'la jolla',
    'morocco',
    'neva ',
    'sideline',
    'silver sur',
    'stream'
]

textile_tags = [
    'spettro',
    'kenzie',
    'omni ash'
]

metal_tags = ['metal']

solid_tags = ['mixer']

geo_tags = ['casablanca']

shaded_tags = [
    'cinder',
    'baize',
    'mulholland',
    'pacific coast',
    'redondo'
]

def get_special(product: ScraperFinishSurface, item):
    att_list = item.get('attributeList', None)
    product.commercial = True
    product.manufacturer_collection = att_list[0].lower()
    product.material = 'luxury vinyl tile'
    look = 'wood'
    for tag in wood_tags:
        if tag in product.manufacturer_style:
            look = 'wood'
    for tag in stone_tags:
        if tag in product.manufacturer_style:
            look = 'stone'
    for tag in natural_tags:
        if tag in product.manufacturer_style:
            look = 'natural pattern'
    for tag in textile_tags:
        if tag in product.manufacturer_style:
            look = 'textile'
    for tag in solid_tags:
        if tag in product.manufacturer_style:
            look = 'solid color'
    for tag in shaded_tags:
        if tag in product.manufacturer_style:
            look = 'shaded / specked'
    if 'metal' in product.manufacturer_style:
        look = 'metal'
    if 'casablanca' in product.manufacturer_style:
        look = 'geometric pattern'
    product.look = look
    dims = att_list[1].split('x')
    if len(dims) > 2:
        product.width = clean_value(dims[0])
        product.length = clean_value(dims[1])
        product.thickness = clean_value(dims[2])
    return product


def get_special_detail(product: ScraperFinishSurface, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.lrv = empty_dict.get('Light Reflectance', None)
    product.install_type = empty_dict.get('Installation Method', None)
    return product
