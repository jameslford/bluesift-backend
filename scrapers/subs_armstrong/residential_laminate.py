from utils.measurements import clean_value
from Scraper.models import ScraperFinishSurface


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


def clean(product: ScraperFinishSurface):
    default_product: ScraperFinishSurface = ScraperFinishSurface.objects.get(pk=product.pk)
    if default_product.length:
        product.length = default_product.length.replace('in.', '').strip()
    if default_product.width:
        product.width = default_product.width.replace('in.', '').strip()
    if default_product.thickness:
        thickness = default_product.thickness.replace('mm', '').strip()
        thickness = round((float(thickness)/25.4), 2)
        product.thickness = str(thickness)
    product.save()
