from config.scripts.measurements import clean_value
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface


def get_special(product, item):
    att_list = item.get('attributeList', None)
    if not att_list:
        return product

    dims = att_list[0].split('x')
    product.width = clean_value(dims[0])
    product.length = clean_value(dims[1])
    product.thickness = clean_value(dims[2])
    product.material = 'laminate flooring'
    product.finish = att_list[1]

    edge, end = att_list[2].split('/')
    product.edge = edge
    product.end = end
    return product


def get_special_detail(product: ScraperFinishSurface, data: dict):
    product.look = data.get('Look', None)
    product.surface_coating = data.get('Finish', None)
    return product
