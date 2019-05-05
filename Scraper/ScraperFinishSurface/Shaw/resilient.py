from ..models import ScraperFinishSurface
from BSscraper.utils import clean_value

def get_special(product: ScraperFinishSurface, item):
    product.floors = True
    product.width = clean_value(item['SizeWidth'])
    product.length = clean_value(item['SizeLength'])
    product.thickness = clean_value(item['Thickness'])
    product.surface_coating = item['Finish']
    # wear_layer_thickness = item['WearLayer']
    # if wear_layer_thickness:
    #     product.surface_coating = wear_layer_thickness + ' ' + product.surface_coating
    finish = item['GlossLevel']
    if finish:
        product.finish = finish + ' gloss'
    surface = item['SurfaceTexture']
    if surface:
        product.look = surface
    product.material = item['ProductCatDesc']
    if not product.material:
        product.material = 'vinyl'
    product.sub_material = item['Look']
    return product
