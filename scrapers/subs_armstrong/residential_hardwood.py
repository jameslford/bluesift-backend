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
    product.material = att_list[1] + ' hardwood'
    product.look = 'wood'
    product.finish = att_list[2]

    edge, end = att_list[3].split('/')
    product.edge = edge
    product.end = end
    return product


def get_special_detail(product: ScraperFinishSurface, data: dict):
    product.sub_material = data.get('Species', None)
    product.surface_coating = data.get('Finish', None)
    return product


def clean(product: ScraperFinishSurface):
    default_product: ScraperFinishSurface = ScraperFinishSurface.objects.get(pk=product.pk)
    if default_product.length:
        product.length = default_product.length.replace('varying lengths:', '').strip()
    product.save()
