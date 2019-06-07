from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from config.scripts.measurements import clean_value


def get_special(product: ScraperFinishSurface, item):
    product.material = 'stone & glass'
    product.width = clean_value(item['WIDTH'])
    product.length = clean_value(item['LengthDimension'])
    product.thickness = clean_value(item['Thickness'])
    product.look = item['Look']
    product.submaterial = item['CeramicConstruction']
    product.finish = item['SurfaceFinish']
    product.cof = item['WetCof']
    return product


def clean(product: ScraperFinishSurface):
    default_product = ScraperFinishSurface.objects.using('scraper_default').get(pk=product.pk)
    default_look = default_product.look
    if not default_look:
        return
    if 'mosaic' in default_look.lower():
        product.shape = 'mosaic'
    if 'glass' in default_look.lower():
        product.sub_material = 'glass'
    product.save()
