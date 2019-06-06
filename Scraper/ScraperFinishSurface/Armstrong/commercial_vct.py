from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from config.scripts.measurements import clean_value


def get_special(product: ScraperFinishSurface, item):
    att_list = item.get('attributeList', None)
    product.commercial = True
    product.material = 'resilient'
    product.sub_material = 'vinyl composite tile'
    collection = att_list[0].lower()
    look = 'shaded / specked'
    if 'feature' in collection:
        look = 'solid color'
    if 'stream' in collection:
        look = 'natural pattern'
    product.look = look
    product.manufacturer_collection = collection
    size_line = att_list[1]
    size_split = size_line.split('<br/>')
    if len(size_split) > 1:
        sizes = [s.split('x') for s in size_line]
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