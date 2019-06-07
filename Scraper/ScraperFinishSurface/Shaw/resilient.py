from ..models import ScraperFinishSurface
from config.scripts.measurements import clean_value

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


def clean(product: ScraperFinishSurface):
    default_product = ScraperFinishSurface.objects.using('scraper_default').get(pk=product.pk)
    product.product_url = product.product_url.replace('+', '')
    if 'LOOSE' in default_product.material:
        product.install_type = 'loose lay'
        product.sub_material = 'luxury vinyl'
    elif 'DRYBAC' in default_product.material:
        product.install_type = 'glue down'
        product.sub_material = 'luxury vinyl'
    elif 'SHEET' in default_product.material:
        product.install_type = 'full spread'
        product.shape = 'continuous'
        product.sub_material = 'vinyl sheet'
    elif 'CLICK' in default_product.material:
        product.sub_material = 'luxury vinyl'
        product.install_type = 'click'
    elif 'EVP' in default_product.sub_material:
        product.sub_material = 'rigid core wpc'
        product.install_type = 'float'
    elif 'WPC' in default_product.sub_material:
        product.sub_material = 'rigid core wpc'
        product.install_type = 'float'
    else:
        product.sub_material = 'rigid core spc'
        product.install_type = 'float'
    product.material = 'resilient'
    product.save()
