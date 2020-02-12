import decimal
from utils.measurements import clean_value
from SpecializedProducts.models import LaminateFlooring
from Scraper.models import ScraperGroup
from psycopg2.extras import NumericRange
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special)


def get_special(product: LaminateFlooring, item):
    product.width = NumericRange(clean_value(item['PlankWidth']))
    product.length = NumericRange(clean_value(item['PlankLength']))
    product.thickness = decimal.Decimal(clean_value(item['Thickness']))
    product.edge = item['EdgeType']
    product.install_type = item['InstallationType']
    product.material = 'laminate flooring'
    product.floors = True
    return product
