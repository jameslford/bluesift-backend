from Scraper.models import ScraperFinishSurface
from utils.measurements import clean_value

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

look_dict = {
    'textile': textile_tags,
    'wood': wood_tags,
    'stone': stone_tags,
    'natural_pattern': natural_tags,
    'metal': metal_tags,
    'solid color': solid_tags,
    'geomateric_pattern': geo_tags,
    'shaded / specked': shaded_tags
}

def get_special(product: ScraperFinishSurface, item):
    att_list = item.get('attributeList', None)
    product.commercial = True
    product.manufacturer_collection = att_list[0].lower()
    product.material = 'resilient'
    product.sub_material = 'luxury vinyl tile'
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


def clean(product: ScraperFinishSurface):
    default_product: ScraperFinishSurface = ScraperFinishSurface.objects.using('scraper_default').get(pk=product.pk)
    product.look = assign_look(default_product)
    if default_product.width:
        product.width = default_product.width.replace('in.', '').strip()
    if default_product.length:
        product.length = default_product.length.replace('in.', '').strip()
    if default_product.thickness:
        thick = default_product.thickness
        thick_split = default_product.thickness.split('<br/>')
        if len(thick_split) > 1:
            thick = thick_split[0]
        product.thickness = thick.replace('in.', '').strip()
    product.save()


def assign_look(default_product: ScraperFinishSurface):
    for look in look_dict:
        tag_list = look_dict[look]
        for tag in tag_list:
            if tag in default_product.manufacturer_style.lower():
                return look
    return 'wood'
