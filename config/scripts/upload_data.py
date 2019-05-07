from django.conf import settings
from Products.models import Product, Manufacturer

def upload_to_production():
    # if settings.ENVIRONMENT != 'staging':
    #     raise Exception('can only be run in staging environment!')
    staging_products = Product.objects.all().select_subclasses()
    staging_dict = staging_products.first().__dict__.copy()
    for line in staging_dict:
        print(line)
    # for staging_product in staging_products:
    #     staging_dict = staging_product.__dict__.copy()
    #     for line in staging_dict:
    #         print(line)
        # model_type = type(staging_product)
        # staging_id = staging_product.bbsku
        # production_product = model_type.objects.using('production').get_or_create(bb_sku=staging_id)
        # staging_dict = 

