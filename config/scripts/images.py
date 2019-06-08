from Scraper.models import ScraperSubgroup, ScraperBaseProduct
from .check_settings import check_local



def get_images(overwrite=False):
    check_local()
    products = None
    if overwrite:
        products = ScraperBaseProduct.objects.using('scraper_default').all()
    else:
        products = ScraperBaseProduct.objects.using('scraper_default').filter(swatch_image_final__isnull=True)
    for product in products:
        product.get_local_images(overwrite)
        product.get_final_images(overwrite)
