from Scraper.models import ScraperDepartment, ScraperManufacturer, ScraperCategory, ScraperSubgroup
from .lists import MODS

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
