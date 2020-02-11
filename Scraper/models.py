from django.db import models, transaction
from django.contrib.contenttypes.models import ContentType
from Products.models import Manufacturer

# Create your models here.
class ScraperGroup(models.Model):
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.SET_NULL,
        null=True,
        )
    category = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        limit_choices_to={'app_label': 'SpecializedProducts'}
        )
    module_name = models.CharField(max_length=70)
    scraped = models.BooleanField(default=False)
    base_url = models.URLField(max_length=2000, null=True, blank=True)

    def path(self):
        return f'utils/{self.manufacturer.label}/{self.module_name}.py'

    @transaction.atomic
    def scrape(self):
        '''get the module and run some arbitrary name i.e Scrape
        curry functions for nested modules (pass in funcs as args)
        get products back and do cleaning/validation here
            -validate same as content type
            -check against existing before saving
            -clean
            -all at once for each group
            beautiful
        '''
        pass


