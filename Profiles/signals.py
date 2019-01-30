from Profiles.models import SupplierProduct
from django.db.models.signals import post_delete
from django.dispatch import receiver


@receiver(post_delete, sender=SupplierProduct)
def recheck_prices(sender, instance, **kwargs):
    instance.product.set_prices()
