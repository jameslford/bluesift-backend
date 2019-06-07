from django.core.management.base import BaseCommand
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from Scraper.models import ScraperManufacturer

class Command(BaseCommand):
    def handle(self, *args, **options):
        # mohawk_url_correction()
        # mohawk_url_correction('scraper_default')
        pass


# def mohawk_url_correction(db='scraper_revised'):
#     mohawk = ScraperManufacturer.objects.using(db).get(name__icontains='mohawk')
#     all_mohawks = ScraperFinishSurface.objects.using(db).filter(subgroup__manufacturer=mohawk)
#     bad_mohawks = all_mohawks.filter(product_url__contains='comhttps')
#     for bad in bad_mohawks:
#         base_string = 'https://www.mohawkflooring.com'
#         new_url = bad.product_url.replace(base_string, '')
#         new_url = base_string + new_url
#         bad.product_url = new_url
#         bad.save(using=db)
#         print(bad.product_url)
