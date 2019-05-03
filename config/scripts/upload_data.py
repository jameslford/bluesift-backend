from django.conf import settings
from Products.models import Product, Manufacturer

def upload_to_production():
    if settings.ENVIRONMENT != 'staging':
        raise Exception('can only be run in staging environment!')
    staging_products = Product.objects.all()
    production_objects = Product.objects.using('production').all()
    for staging_product in staging_products:
        staging_id = staging_product.bbsku
        staging_sub_product = staging_product.content

        production_product = production_objects.get_or_create(bb_sku=staging_id)
