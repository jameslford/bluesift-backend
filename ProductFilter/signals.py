from .models import ProductFilter
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_save, sender=ProductFilter)
def refresh_qi_postsave(sender, instance: ProductFilter, dispatch_uid="refresh_filter_qis", **kwargs):
    print('signal received')
    instance.refresh_QueryIndex()
