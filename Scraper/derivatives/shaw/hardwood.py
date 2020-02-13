from psycopg2.extras import NumericRange
from utils.measurements import clean_value
from SpecializedProducts.models import Hardwood
from Scraper.models import ScraperGroup
from .base import scrape

def run(group: ScraperGroup):
    scrape(group, get_special)

def get_special(product: Hardwood, item):
    product.floors = True
    product.width = NumericRange(clean_value(item['PlankWidth']))
    product.length = NumericRange(clean_value(item['PlankLength']))
    product.install_type = item['InstallationType']
    product.shade_variation = item['ColorVariationRatingShortDesc']
    gloss = None
    gloss_level = item['GlossLevel']
    if gloss_level:
        if gloss_level < 20:
            gloss = 'matte'
        elif gloss_level < 56:
            gloss = 'semi-gloss'
        else:
            gloss = 'high gloss'
    product.finish = gloss
    product.composition = item['Construction']
    product.species = item['Species']
    return product
