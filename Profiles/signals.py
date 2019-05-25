from Profiles.models import SupplierProduct
from ProductFilter.models import DetailBuilder
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_delete, sender=SupplierProduct)
def recheck_prices(sender, instance: SupplierProduct, **kwargs):
    instance.product.set_prices()
    instance.product.invalidate_queries()
    instance.product.set_locations()
    builder = DetailBuilder(instance.product.pk)
    builder.get_reponse(update=True)


@receiver(post_save, sender=SupplierProduct)
def refresh_after_save(sender, instance: SupplierProduct, **kwargs):
    instance.product.set_prices()
    instance.product.invalidate_queries()
    instance.product.set_locations()
    builder = DetailBuilder(instance.product.pk)
    builder.get_reponse(update=True)
