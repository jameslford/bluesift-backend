from Scraper.models import ScraperFinishSurface
from utils.measurements import clean_value

stone_tags = [
    'slate',
    'concrete',
    'travertine'
]


def get_special(product: ScraperFinishSurface, item):
    att_list = item.get('attributeList', None)
    product.manufacturer_collection = att_list[0]
    look = 'wood'
    for tag in stone_tags:
        if tag in product.manufacturer_style:
            look = 'stone'
    product.look = look
    width, length, thickness = att_list[1].split('x')
    product.width = clean_value(width)
    product.length = clean_value(length)
    product.thickness = clean_value(thickness)
    product.material = 'resilient'
    product.sub_material = 'rigid core'
    product.commercial = True
    return product

def get_special_detail(product: ScraperFinishSurface, empty_dict: dict):
    product.finish = empty_dict.get('gloss', None)
    product.install_type = empty_dict.get('Installation Method', None)
    product.sub_material = empty_dict.get('Wood Species', None)
    product.sqft_per_carton = empty_dict.get('Coverage Per Carton', None)
    edge_end = empty_dict.get('Edge Detail', None)
    end = None
    edge = None
    if edge_end:
        split = edge_end.split('/')
        if len(split) > 1:
            edge, end = split
        else:
            edge = edge_end
            end = edge_end
    product.end = end
    product.edge = edge
    return product
