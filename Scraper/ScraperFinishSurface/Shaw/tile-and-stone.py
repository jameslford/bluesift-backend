from ..models import ScraperFinishSurface
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


def clean():
    from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
    default_tiles = ScraperFinishSurface.objects.using('scraper_default').filter(material='stone & glass')
    revised_tiles = ScraperFinishSurface.objects.filter(material='stone & glass')
    for tile in default_tiles:
        default_look = tile.look
        revised_product: ScraperFinishSurface = revised_tiles.get(pk=tile.pk)
        if not default_look:
            continue
        if 'mosaic' in default_look.lower():
            revised_product.shape = 'mosaic'
        if 'glass' in default_look.lower():
            revised_product.sub_material = 'glass'
        revised_product.save()