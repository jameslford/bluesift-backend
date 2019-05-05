from ScraperFinishSurface.models import ScraperFinishSurface
from BSscraper.utils import clean_value
from bs4 import BeautifulSoup

textile_tags = ['linen', 'tweed']
wood_tags = ['oak', 'maple', 'cherry', 'bamboo', 'walnut', 'timber', 'mallorca', 'echo']
stone_tags = ['stone', 'fossil', 'slate', 'travertini']
metal_tags = ['steel']


def get_special(product: ScraperFinishSurface, item):
    product.material = 'heterogeneous sheet vinyl'
    product.commercial = True
    att_list = item.get('attributeList', None)
    collection = att_list[0]
    look = 'shaded / specked'
    if 'ambigu' in collection:
        look = 'textile'
    elif 'stoneRun' in collection:
        look = 'stone'
    elif 'timber' in collection:
        look = 'wood'
    else:
        for tag in textile_tags:
            if tag in product.manufacturer_style:
                look = 'textile'
        for tag in wood_tags:
            if tag in product.manufacturer_style:
                look = 'wood'
        for tag in stone_tags:
            if tag in product.manufacturer_style:
                look = 'stone'
        if 'steel' in product.manufacturer_style:
            look = 'metal'

    product.look = look
    width, length, thickness = att_list[1].split('x')
    product.width = clean_value(width)
    product.length = clean_value(length)
    product.thickness = clean_value(thickness)
    return product


def get_special_detail(product: ScraperFinishSurface, empty_dict: dict):
    gloss = empty_dict.get('gloss', None)
    lrv = empty_dict.get('Light Reflectance', None)
    install_type = empty_dict.get('Installation Method', None)
    product.finish = gloss
    product.install_type = install_type
    product.lrv = lrv
    return product
