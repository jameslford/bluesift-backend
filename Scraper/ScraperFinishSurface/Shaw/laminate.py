from ..models import ScraperFinishSurface
from BSscraper.utils import clean_value

def get_special(product: ScraperFinishSurface, item):
    product.width = clean_value(item['PlankWidth'])
    product.length = clean_value(item['PlankLength'])
    product.thickness = clean_value(item['Thickness'])
    product.edge = item['EdgeType']
    product.install_type = item['InstallationType']
    product.material = 'laminate flooring'
    product.floors = True
    return product
