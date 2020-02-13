from psycopg2.extras import NumericRange
from SpecializedProducts.models import TileAndStone
from utils.measurements import clean_value
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special)

def get_special(product: TileAndStone, item):
    product.width = NumericRange(clean_value(item['WIDTH']))
    product.length = NumericRange(clean_value(item['LengthDimension']))
    look = item.get('Look', '')
    product.look = look
    product.material_type = item['CeramicConstruction']
    product.finish = item['SurfaceFinish']
    product.cof = item['WetCof']
    if look and 'MOSAIC' in look:
        product.shape = 'mosaic'
    if look and 'GLASS' in look:
        product.material_type = 'glass'
    return product
