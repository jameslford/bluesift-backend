import os
import datetime
import glob
from stat import S_ISREG, ST_CTIME, ST_MODE
from django.conf import settings
from django.db import transaction
from django.core.management import call_command
from config.custom_storage import MediaStorage
from Scraper.models import (
    ScraperBaseProduct,
    ScraperCategory,
    ScraperSubgroup,
    ScraperManufacturer,
    ScraperDepartment
    )
from Scraper.ScraperCleaner.models import ScraperCleaner
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from Products.models import Product
from ProductFilter.models import ProductFilter
from .lists import MODS
from .check_settings import exclude_production, check_staging, check_local
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
        print(department.name)
        department.save(using='scraper_revised')
        print(department.name + ' saved')
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

# @transaction.atomic()
def run_stock_clean():
    for group in ScraperSubgroup.objects.filter(cleaned=False):
        group.run_stock_clean()


@transaction.atomic()
def run_scraper_cleaners():
    for cleaner in ScraperCleaner.objects.all():
        cleaner.run_clean()


# def delete_scraper_revised():
#     ScraperManufacturer.objects.all().delete()
#     ScraperDepartment.objects.all().delete()
#     ScraperCategory.objects.all().delete()
#     ScraperSubgroup.objects.all().delete()
#     ScraperBaseProduct.objects.all().delete()
#     ScraperAggregateProductRating.objects.all().delete()


def initialize_data():
    for mod in MODS:
        manufacturer = ScraperManufacturer.objects.db_manager('scraper_default').get_or_create(name=mod[0])[0]
        manufacturer = ScraperManufacturer.objects.using('scraper_default').get(name=mod[0])
        department = ScraperDepartment.objects.db_manager('scraper_default').get_or_create(name=mod[1])[0]
        department = ScraperDepartment.objects.using('scraper_default').get(name=mod[1])
        category = ScraperCategory.objects.db_manager('scraper_default').get_or_create(name=mod[2], department=department)[0]
        category = ScraperCategory.objects.using('scraper_default').get(name=mod[2], department=department)
        subgroup, subgroup_created = ScraperSubgroup.objects.db_manager('scraper_default').get_or_create(
            manufacturer=manufacturer,
            category=category,
            )
        if subgroup_created:
            subgroup.base_scraping_url = mod[3]
            subgroup.save()


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
    # for database in local_dbs:
    for database in ['default', 'scraper_default', 'scraper_revised']:
        env_path = f'{current_path}\\z_backups\\{environment}\\{database}\\'
        if not os.path.exists(env_path):
            os.makedirs(env_path)
        filename = f'{env_path}{dt_string}.json'
        db_arg = f'--database={database}'
        with open(filename, 'w+') as f:
            call_command('dumpdata', db_arg, stdout=f)


def clean_backups():
    """gets sorted array of files per <current_environment>/<database>
    and uploads to aws media. then deletes file from local
    """
    environment = settings.ENVIRONMENT
    from config.settings.local import DATABASES as local_dbs
    current_path = os.getcwd()
    s3 = MediaStorage()
    for database in local_dbs:
        dirpath = f'{current_path}\\z_backups\\{environment}\\{database}\\'
        entries = (os.path.join(dirpath, fn) for fn in os.listdir(dirpath))
        entries = ((os.stat(path), path) for path in entries)
        entries = ((stat[ST_CTIME], path) for stat, path in entries if S_ISREG(stat[ST_MODE]))
        for cdate, path in sorted(entries)[:-1]:
            with open(path, 'rb') as f:
                name = f'db_backups\\{environment}\\{database}\\{os.path.basename(path)}'
                s3.save(name, f)
                f.close()
                os.remove(path)


def migrate_all():
    from config.settings.local import DATABASES as local_dbs
    for database in local_dbs:
        db_arg = f'--database={database}'
        call_command('migrate', db_arg)


def refresh_filters():
    p_filters = ProductFilter.objects.all()
    for p_filter in p_filters:
        p_filter.save()


@transaction.atomic()
def reset_supplier_products():
    from UserProducts.models import RetailerProduct
    for supplier_product in RetailerProduct.objects.all():
        supplier_product.reset_product()


@transaction.atomic()
def refresh_default_database():
    Product.objects.all().delete()
    assign_label_color()
    revised_to_default()
    refresh_filters()
    reset_supplier_products()


@transaction.atomic()
def load_from_backup():
    exclude_production()
    if os.name == 'nt':
        path = 'z_backups\\local\\scraper_default\\*.json'
    else:
        path = 'z_backups/local/scraper_default/*.json'
    backups = glob.glob(path)
    latest = max(backups, key=os.path.getctime)
    call_command('loaddata', latest, '--database=scraper_default')


@transaction.atomic()
def staging_revised_to_local_revised():
    check_local()
    # departments = ScraperDepartment.objects.using('staging_scraper_default').all()
    # manufacturers = ScraperManufacturer.objects.using('staging_scraper_default').all()
    # categories = ScraperCategory.objects.using('staging_scraper_default').all()
    # subgroups = ScraperSubgroup.objects.using('staging_scraper_default').all()
    # fs_products = ScraperFinishSurface.objects.using('staging_scraper_default').all()
    # scraper_cleaners = ScraperCleaner.objects.using('staging_scraper_default').all()

    # for department in departments:
    #     department.save(using='scraper_default')
    # ScraperManufacturer.objects.db_manager('scraper_default').bulk_create(list(manufacturers))
    # ScraperCategory.objects.db_manager('scraper_default').bulk_create(list(categories))
    # ScraperSubgroup.objects.db_manager('scraper_default').bulk_create(list(subgroups))
    # ScraperFinishSurface.objects.db_manager('scraper_default').bulk_create(list(fs_products))
    # ScraperCleaner.objects.db_manager('scraper_default').bulk_create(list(scraper_cleaners))

    # for manufacturer in manufacturers:
    #     manufacturer.save(using='scraper_revised')
    # for category in categories:
    #     category.save(using='scraper_revised')
    # for group in subgroups:
    #     group.save(using='scraper_revised')
    # for product in products:
    #     product.save(using='scraper_revised')
