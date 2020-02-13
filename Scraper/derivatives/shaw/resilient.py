from psycopg2.extras import NumericRange
from Scraper.models import ScraperGroup
from SpecializedProducts.models import Resilient
from utils.measurements import clean_value
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special)


def get_special(product: Resilient, item):
    product.floors = True
    product.width = NumericRange(clean_value(item['SizeWidth']))
    product.length = NumericRange(clean_value(item['SizeLength']))
    product.surface_coating = item['Finish']
    wear_layer_thickness = item.get('WearLayer')
    if wear_layer_thickness:
        product.surface_coating = wear_layer_thickness + ' ' + product.surface_coating
    finish = item['GlossLevel']
    if finish:
        product.finish = finish + ' gloss'
    surface = item['SurfaceTexture']
    if surface:
        product.look = surface
    product.material_type = item['ProductCatDesc']
    if not product.material_type:
        product.material_type = item['Look']
    product = clean(product)
    return product


def clean(product: Resilient):
    product.product_url = product.product_url.replace('+', '')
    if 'LOOSE' in product.material_type:
        product.install_type = 'loose lay'
        product.material_type = 'luxury vinyl'
    elif 'DRYBAC' in product.material_type:
        product.install_type = 'glue down'
        product.material_type = 'luxury vinyl'
    elif 'SHEET' in product.material_type:
        product.install_type = 'full spread'
        product.shape = 'continuous'
        product.material_type = 'vinyl sheet'
    elif 'CLICK' in product.material_type:
        product.material_type = 'luxury vinyl'
        product.install_type = 'click'
    elif 'EVP' in product.material_type:
        product.material_type = 'rigid core wpc'
        product.install_type = 'float'
    elif 'WPC' in product.material_type:
        product.material_type = 'rigid core wpc'
        product.install_type = 'float'
    else:
        product.material_type = 'rigid core spc'
        product.install_type = 'float'
    return product

    # if product.thickness:
    #     thick_split = product.thickness.split('/')
    #     num = decimal.Decimal(thick_split[0])
    #     dem = decimal.Decimal(thick_split[1])
    #     thickness = round((num / dem), 3)
    #     product.thickness = str(thickness)