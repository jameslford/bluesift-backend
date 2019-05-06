from Scraper.models import ScraperBaseProduct, ScraperCategory, ScraperSubgroup, ScraperManufacturer, ScraperDepartment

def populate_db():
    departments = ScraperDepartment.objects.all()
    manufacturers = ScraperManufacturer.objects.all()
    categories = ScraperCategory.objects.all()
    subgroups = ScraperSubgroup.objects.all()
    for department in departments:
        department.save(using='scraper_revised', force_insert=True)
    for manufacturer in manufacturers:
        manufacturer.save(using='scraper_revised', force_insert=True)
    for category in categories:
        category.save(using='scraper_revised', force_insert=True)
    for group in subgroups:
        group.save(using='scraper_revised', force_insert=True)
    original_groups = ScraperSubgroup.objects.all()
    for og in original_groups:
        products = og.products.select_subclasses().all()
        for product in products:
            product.save(using='scraper_revised', force_insert=True)


def delete_all():
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


def clean():
    pass
