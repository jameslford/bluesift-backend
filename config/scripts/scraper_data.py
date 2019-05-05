from Scraper.models import (
    ScraperManufacturer,
    ScraperDepartment,
    ScraperCategory,
    ScraperSubgroup,
    ScraperAggregateProductRating
)
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

def delete_data():
    ScraperManufacturer.objects.all().delete()
    ScraperDepartment.objects.all().delete()
    ScraperCategory.objects.all().delete()
    ScraperSubgroup.objects.all().delete()
    # ScraperFinishSurface.objects.all().delete()
    ScraperAggregateProductRating.objects.all().delete()
