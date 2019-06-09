from Scraper.models import ScraperSubgroup, ScraperBaseProduct
from .check_settings import exclude_production



def get_images(overwrite=False):
    exclude_production()
    products = None
    if overwrite:
        products = ScraperBaseProduct.objects.using('scraper_default').all()
    else:
        products = ScraperBaseProduct.objects.using('scraper_default').filter(swatch_image_final__isnull=True)
    for product in products:
        product.get_local_images(overwrite)
        product.get_final_images(overwrite)
