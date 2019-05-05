from Scraper.models import ScraperBaseProduct, ScraperCategory, ScraperSubgroup, ScraperManufacturer, ScraperDepartment

def populate_db():
    departments = ScraperDepartment.objects.all()
    manufacturers = ScraperManufacturer.objects.all()
    categories = ScraperCategory.objects.all()
    subgroups = ScraperSubgroup.objects.all()
    for department in departments:
        department.save(using='revised', force_insert=True)
    for manufacturer in manufacturers:
        manufacturer.save(using='revised', force_insert=True)
    for category in categories:
        category.save(using='revised', force_insert=True)
    for group in subgroups:
        group.save(using='revised', force_insert=True)
    original_groups = ScraperSubgroup.objects.all()
    for og in original_groups:
        products = og.products.select_subclasses().all()
        for product in products:
            product.save(using='revised', force_insert=True)


def delete_all():
    departments = ScraperDepartment.objects.using('revised').all()
    manufacturers = ScraperManufacturer.objects.using('revised').all()
    categories = ScraperCategory.objects.using('revised').all()
    subgroups = ScraperSubgroup.objects.using('revised').all()
    for group in subgroups:
        products = group.products.select_subclasses()
        products.all().delete()
    subgroups.delete()
    categories.delete()
    departments.delete()
    manufacturers.delete()
