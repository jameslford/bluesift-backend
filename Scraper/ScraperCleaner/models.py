from django.db import models
from django.contrib.postgres import fields as pg_fields
from Scraper.models import ScraperSubgroup, ScraperBaseProduct

class ScraperCleaner(models.Model):
    subgroup_manufacturer_name = models.CharField(max_length=200, null=True, blank=True)
    subgroup_category_name = models.CharField(max_length=200, null=True, blank=True)
    field_name = models.CharField(max_length=200, null=True, blank=True)
    initial_value = models.CharField(max_length=200, null=True, blank=True)
    new_value = models.CharField(max_length=200, null=True, blank=True)


    def __str__(self):
        return (
            f'{self.subgroup_manufacturer_name} {self.subgroup_category_name} '
            f'{self.field_name} {self.initial_value}'
        )

    def run_clean(self):
        default_subgroups = ScraperSubgroup.objects.using('scraper_default').all()
        subgroup: ScraperSubgroup = default_subgroups.filter(
            manufacturer__name=self.subgroup_manufacturer_name,
            category__name=self.subgroup_category_name
            ).first()
        if not subgroup:
            return
        argument = {self.field_name: self.initial_value}
        model_type = subgroup.get_prod_type()
        default_products = model_type.objects.using('scraper_default').filter(**argument)
        if not default_products:
            return
        pks = [product.pk for product in default_products]
        revised_products = ScraperBaseProduct.objects.using('scraper_revised').filter(pk__in=pks).select_subclasses()
        if not revised_products:
            return
        for product in revised_products:
            setattr(product, self.field_name, self.new_value)
            product.save()
        self.save()


class CleanerUtility:

    def __init__(self, value: str):
        self.value = value

    def lower_values(self):
        if self.value:
            return self.value.lower()
        return self.value

    def strip_values(self):
        if self.value:
            return self.value.strip()
        return self.value

    def fraction_to_decimal_values(self):
        new_val = self.value.split('/')
        if len(new_val) < 2:
            raise Exception('not a fraction')

    @classmethod
    def create_scraper_cleaner(cls, product_pk: str, field: str, new_value: str):
        default_product = ScraperBaseProduct.objects.using('scraper_default').filter(pk=product_pk).select_subclasses().first()
        initial_value = getattr(default_product, field)
        scraper_cleaner = ScraperCleaner.objects.get_or_create(
            subgroup_manufacturer_name=default_product.subgroup.manufacturer.name,
            subgroup_category_name=default_product.subgroup.category.name,
            field_name=field,
            initial_value=initial_value
        )[0]
        scraper_cleaner.new_value = new_value
        scraper_cleaner.save()
        print('cleaner saved')

    def __call__(self, function: str):
        func = getattr(self, function)
        if not func:
            raise Exception('no matching function')
        return func()

    @classmethod
    def get_functions_list(cls):
        return [method_name for method_name in dir(cls) if callable(getattr(cls, method_name)) and 'values' in method_name]
