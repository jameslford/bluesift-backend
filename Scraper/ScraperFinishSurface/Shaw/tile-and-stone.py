from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from config.scripts.measurements import clean_value


def get_special(product: ScraperFinishSurface, item):
    product.material = 'stone & glass'
    product.width = clean_value(item['WIDTH'])
    product.length = clean_value(item['LengthDimension'])
    product.thickness = clean_value(item['Thickness'])
    product.look = item['Look']
    product.sub_material = item['CeramicConstruction']
    product.finish = item['SurfaceFinish']
    product.cof = item['WetCof']
    return product



def clean(product: ScraperFinishSurface):
    default_product = ScraperFinishSurface.objects.using('scraper_default').get(pk=product.pk)
    default_look = default_product.look
    if not default_look:
        return
    if 'MOSAIC' in default_look:
        product.shape = 'mosaic'
    if 'GLASS' in default_look:
        product.sub_material = 'glass'
    product.save()
