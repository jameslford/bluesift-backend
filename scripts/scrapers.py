from django.contrib.contenttypes.models import ContentType
from Scraper.models import ScraperGroup
from Scraper.initial_groups import groups
from Products.models import Manufacturer


def scrape(update=False):
    if update:
        scrapers = ScraperGroup.objects.all()
    else:
        scrapers = ScraperGroup.objects.filter(scraped=False)
    for scraper in scrapers:
        scraper.scrape()


def create_scrapers():
    for group in groups:

        manufacturer = Manufacturer.objects.get_or_create(label=group[0])[0]
        base_url = group[1]
        category = ContentType.objects.get_for_model(group[2])
        module_name = group[3]

        ScraperGroup.objects.get_or_create(
            manufacturer=manufacturer,
            base_url=base_url,
            category=category,
            module_name=module_name
            )
