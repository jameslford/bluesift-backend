from django.db import models
from django.contrib.postgres import fields as pg_fields
from Scraper.models import ScraperSubgroup, ScraperBaseProduct

class ScraperCleaner(models.Model):
    subgroup_manufacturer_name = models.CharField(max_length=200, null=True, blank=True)
    subgroup_category_name = models.CharField(max_length=200, null=True, blank=True)
    product_pks = pg_fields.ArrayField(
        models.UUIDField(null=True, blank=True),
        null=True,
        blank=True
        )
    field_name = models.CharField(max_length=200, null=True, blank=True)
    initial_value = models.CharField(max_length=200, null=True, blank=True)
    new_value = models.CharField(max_length=200, null=True, blank=True)

    class Meta:
        unique_together = [[
            'subgroup_manufacturer_name',
            'subgroup_category_name',
            'field_name',
            'initial_value'
            ]]

    def refresh_and_clean(self):
        default_subgroups = ScraperSubgroup.objects.using('scraper_default').all()
        subgroup = default_subgroups.filter(
            manufacturer__name=self.subgroup_manufacturer_name,
            category__name=self.subgroup_category_name
            ).first()
        if not subgroup:
            return
        argument = {self.field_name: self.initial_value}
        default_products = subgroup.products.filter(**argument)
        if not default_products:
            return
        pks = [product.pk for product in default_products]
        revised_products = ScraperBaseProduct.objects.filter(pk__in=pks).select_subclasses()
        if not revised_products:
            return
        self.product_pks = pks
        for product in revised_products:
            setattr(product, self.field_name, self.new_value)
            product.save()
        self.save()

    def clean(self):
        revised_products = ScraperBaseProduct.objects.using('scraper_revised').filter(pk__in=self.product_pks).select_subclasses()
        for product in revised_products:
            setattr(product, self.field_name, self.new_value)
            product.save()
