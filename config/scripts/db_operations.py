import os
import datetime
from django.conf import settings
from django.db import transaction
from django.core.management import call_command
from Scraper.models import (
    ScraperBaseProduct,
    ScraperCategory,
    ScraperSubgroup,
    ScraperManufacturer,
    ScraperDepartment,
    ScraperAggregateProductRating
    )
from Products.models import Product
from ProductFilter.models import ProductFilter
from .lists import MODS
from .check_settings import exclude_production
from .colors import assign_label_color

@transaction.atomic(using='scraper_revised')
def scraper_to_revised():
    exclude_production()
    departments = ScraperDepartment.objects.using('scraper_default').all()
    manufacturers = ScraperManufacturer.objects.using('scraper_default').all()
    categories = ScraperCategory.objects.using('scraper_default').all()
    subgroups = ScraperSubgroup.objects.using('scraper_default').all()
    products = ScraperBaseProduct.objects.using('scraper_default').all().select_subclasses()
    for department in departments:
        department.save(using='scraper_revised')
    for manufacturer in manufacturers:
        manufacturer.save(using='scraper_revised')
    for category in categories:
        category.save(using='scraper_revised')
    for group in subgroups:
        group.save(using='scraper_revised')
    for product in products:
        product.save(using='scraper_revised')

@transaction.atomic()
def revised_to_default():
    exclude_production()
    departments = ScraperDepartment.objects.using('scraper_revised').all()
    for department in departments:
        department.add_to_default()

@transaction.atomic(using='production')
def staging_to_production():
    if settings.ENVIRONMENT != 'staging':
        raise Exception('can only be run in staging environment!')
    staging_products = Product.objects.all().select_subclasses()
    for staging_product in staging_products:
        staging_product.save(using='production')


def clean_revised():
    assign_label_color()


def delete_scraper_revised():
    ScraperManufacturer.objects.all().delete()
    ScraperDepartment.objects.all().delete()
    ScraperCategory.objects.all().delete()
    ScraperSubgroup.objects.all().delete()
    ScraperBaseProduct.objects.all().delete()
    ScraperAggregateProductRating.objects.all().delete()


def initialize_data():
    for mod in MODS:
        manufacturer = ScraperManufacturer.objects.using('scraper_default').get_or_create(name=mod[0])[0]
        department = ScraperDepartment.objects.using('scraper_default').get_or_create(name=mod[1])[0]
        category = ScraperCategory.objects.using('scraper_default').get_or_create(name=mod[2], department=department)[0]
        subgroup = ScraperSubgroup.objects.using('scraper_default').get_or_create(
            manufacturer=manufacturer,
            category=category,
            base_scraping_url=mod[3]
            )[0]


def scrape(overwrite=False):
    for group in ScraperSubgroup.objects.using('scraper_default').all():
        if overwrite:
            group.get_data()
        elif not group.scraped:
            group.get_data()


def backup_db():
    now = datetime.datetime.now()
    dt_string = now.strftime('%Y-%m-%d-%H-%M-%S')
    environment = settings.ENVIRONMENT
    current_path = os.getcwd()
    for database in settings.DATABASES:
        path = f'{current_path}\\z_backups\\{environment}_{database}_{dt_string}.json'
        db_arg = f'--database={database}'
        with open(path, 'w+') as f:
            call_command('dumpdata', db_arg, stdout=f)


def migrate_all():
    for database in settings.DATABASES:
        db_arg = f'--database={database}'
        call_command('migrate', db_arg)


def refresh_filters():
    p_filters = ProductFilter.objects.all()
    for p_filter in p_filters:
        p_filter.save()


def refresh_default_database():
    Product.objects.all().delete()
    revised_to_default()
    assign_label_color()
    refresh_filters()
