import importlib
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
        return f'Scraper.derivatives.{self.manufacturer.label}.{self.module_name}'

    def get_model(self):
        return self.category.model_class()

    @transaction.atomic
    def scrape(self):
        path = self.path()
        mod = importlib.import_module(path)
        mod.run(self)
        self.scraped = True
        self.save()
