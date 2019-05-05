from ..models import ScraperFinishSurface
from BSscraper.utils import clean_value

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
