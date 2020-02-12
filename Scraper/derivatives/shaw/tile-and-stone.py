import decimal
from SpecializedProducts.models import TileAndStone
from utils.measurements import clean_value
from psycopg2.extras import NumericRange


def get_special(product: TileAndStone, item):
    product.width = NumericRange(clean_value(item['WIDTH']))
    product.length = NumericRange(clean_value(item['LengthDimension']))
    product.thickness = decimal.Decimal(clean_value(item['Thickness']))
    product.look = item['Look']
    product.material_type = item['CeramicConstruction']
    product.finish = item['SurfaceFinish']
    product.cof = item['WetCof']
    if 'MOSAIC' in item['look']:
        product.shape = 'mosaic'
    if 'GLASS' in item['look']:
        product.material_type = 'glass'
    return product
