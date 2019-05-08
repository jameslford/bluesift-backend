from Scraper.models import (
    ScraperBaseProduct,
    ScraperCategory,
    ScraperSubgroup,
    ScraperManufacturer,
    ScraperDepartment,
    ScraperAggregateProductRating
    )
from Products.models import Product
from django.conf import settings
from .lists import MODS
from .check_settings import exclude_production
from .colors import assign_label_color

def scraper_to_revised():
    exclude_production()
    departments = ScraperDepartment.objects.all()
    manufacturers = ScraperManufacturer.objects.all()
    categories = ScraperCategory.objects.all()
    subgroups = ScraperSubgroup.objects.all()
    for department in departments:
        department.save(using='scraper_revised')
    for manufacturer in manufacturers:
        manufacturer.save(using='scraper_revised')
    for category in categories:
        category.save(using='scraper_revised')
    for group in subgroups:
        group.save(using='scraper_revised')
    original_groups = ScraperSubgroup.objects.all()
    for og in original_groups:
        products = og.products.select_subclasses().all()
        for product in products:
            product.save(using='scraper_revised')

def revised_to_default():
    exclude_production()
    departments = ScraperDepartment.objects.using('scraper_revised').all()
    for department in departments:
        department.add_to_default()


def staging_to_production():
    if settings.ENVIRONMENT != 'staging':
        raise Exception('can only be run in staging environment!')
    staging_products = Product.objects.all().select_subclasses()
    for staging_product in staging_products:
        model_type = type(staging_product)
        staging_id = staging_product.bb_sku
        production_product = model_type.objects.using('production').get_or_create(bb_sku=staging_id)[0]
        production_product.swatch_image = staging_product.swatch_image
        production_product.room_scene = staging_product.room_scene
        production_product.tiling_image = staging_product.tiling_image
        staging_dict = staging_product.__dict__.copy()
        del staging_dict['_state']
        del staging_dict['swatch_image']
        del staging_dict['room_scene']
        del staging_dict['tiling_image']
        del staging_dict['bb_sku']
        production_product(**staging_dict)
        production_product.save()


def clean_revised():
    assign_label_color()


def delete_revised():
    exclude_production()
    departments = ScraperDepartment.objects.using('scraper_revised').all()
    manufacturers = ScraperManufacturer.objects.using('scraper_revised').all()
    categories = ScraperCategory.objects.using('scraper_revised').all()
    subgroups = ScraperSubgroup.objects.using('scraper_revised').all()
    for group in subgroups:
        products = group.products.select_subclasses()
        products.all().delete()
    subgroups.delete()
    categories.delete()
    departments.delete()
    manufacturers.delete()


def delete_scraper_default():
    ScraperManufacturer.objects.all().delete()
    ScraperDepartment.objects.all().delete()
    ScraperCategory.objects.all().delete()
    ScraperSubgroup.objects.all().delete()
    ScraperBaseProduct.objects.all().delete()
    ScraperAggregateProductRating.objects.all().delete()


def initialize_data():
    for mod in MODS:
        manufacturer = ScraperManufacturer.objects.get_or_create(name=mod[0])[0]
        department = ScraperDepartment.objects.get_or_create(name=mod[1])[0]
        category = ScraperCategory.objects.get_or_create(name=mod[2], department=department)[0]
        subgroup = ScraperSubgroup.objects.get_or_create(
            manufacturer=manufacturer,
            category=category,
            base_scraping_url=mod[3]
            )[0]


def scrape_new():
    for group in ScraperSubgroup.objects.all():
        if not group.scraped:
            group.get_data()


def scrape_all():
    for group in ScraperSubgroup.objects.all():
        group.get_data()
