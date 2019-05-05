from Scraper.models import ScraperSubgroup
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


def get_images():
    check_local()
    subgroups = ScraperSubgroup.objects.all()
    for group in subgroups:
        products = group.products.all()
        for product in products:
            product.get_local_images()
            product.get_final_images()