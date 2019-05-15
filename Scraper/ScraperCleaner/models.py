from django.db import models
from Scraper.models import ScraperSubgroup

class ScraperCleaner(models.Model):
    subgroup_manufacturer_name = models.CharField(max_length=200, null=True, blank=True)
    subgroup_category_name = models.CharField(max_length=200, null=True, blank=True)
    field = models.CharField(max_length=200, null=True, blank=True)
    initial_value = models.CharField(max_length=200, null=True, blank=True)
    new_value = models.CharField(max_length=200, null=True, blank=True)
