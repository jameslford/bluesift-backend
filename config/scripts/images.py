from Scraper.models import ScraperSubgroup, ScraperBaseProduct
from .check_settings import check_local


def get_local_images():
    check_local()
    subgroups = ScraperSubgroup.objects.all()
    for group in subgroups:
        products = group.products.all()
        for product in products:
            product.get_local_images()

def get_final_images():
    check_local()
    subgroups = ScraperSubgroup.objects.all()
    for group in subgroups:
        products = group.products.all()
        for product in products:
            product.get_final_images()


def get_images(overwrite=False):
    check_local()
    subgroups = None
    if overwrite:
        subgroups = ScraperSubgroup.objects.using('scraper_default').all()
    else:
        subgroups = ScraperSubgroup.objects.using('scraper_default').filter(scraped=False)
    for group in subgroups:
        products = group.products.all()
        for product in products:
            product.get_local_images(overwrite)
            product.get_final_images(overwrite)
