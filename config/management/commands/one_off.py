from django.core.management.base import BaseCommand
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from Scraper.models import ScraperManufacturer

class Command(BaseCommand):
    def handle(self, *args, **options):
        # mohawk_url_correction()
        # mohawk_url_correction('scraper_default')
        clean_shaw_resilients()


def mohawk_url_correction(db='scraper_revised'):
    mohawk = ScraperManufacturer.objects.using(db).get(name__icontains='mohawk')
    all_mohawks = ScraperFinishSurface.objects.using(db).filter(subgroup__manufacturer=mohawk)
    bad_mohawks = all_mohawks.filter(product_url__contains='comhttps')
    for bad in bad_mohawks:
        base_string = 'https://www.mohawkflooring.com'
        new_url = bad.product_url.replace(base_string, '')
        new_url = base_string + new_url
        bad.product_url = new_url
        bad.save(using=db)
        print(bad.product_url)


def clean_shaw_resilients():
    shaw = ScraperManufacturer.objects.get(name__icontains='shaw')
    shaw_products = ScraperFinishSurface.objects.filter(subgroup__manufacturer=shaw)
    shaw_resilients = shaw_products.filter(subgroup__category__name__icontains='resilient')
    for res in shaw_resilients:
        res: ScraperFinishSurface = res
        res.product_url = res.product_url.replace('+', '')
        if 'LOOSE' in res.material:
            res.install_type = 'loose lay'
            res.sub_material = 'luxury vinyl'
        elif 'DRYBAC' in res.material:
            res.install_type = 'glue down'
            res.sub_material = 'luxury vinyl'
        elif 'SHEET' in res.material:
            res.install_type = 'full spread'
            res.shape = 'continuous'
            res.sub_material = 'vinyl sheet'
        elif 'CLICK' in res.material:
            res.sub_material = 'luxury vinyl'
            res.install_type = 'click'
        elif 'EVP' in res.sub_material:
            res.sub_material = 'rigid core wpc'
            res.install_type = 'float'
        elif 'WPC' in res.sub_material:
            res.sub_material = 'rigid core wpc'
            res.install_type = 'float'
        else:
            res.sub_material = 'rigid core spc'
            res.install_type = 'float'
        res.material = 'resilient'
        res.save()


        
        
        
        
        
