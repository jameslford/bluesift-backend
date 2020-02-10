import decimal
import numpy as np
from django.db import transaction
from django.db.models import QuerySet, FloatField
from django.db.models.functions import Cast
from SpecializedProducts.models import FinishSurface
# from django.db.models.functions import Lower

def assign_size():
    products = FinishSurface.objects.all()
    set_size(products)
    cluster_sizes(products)

@transaction.atomic()
def set_size(products: QuerySet):
    for product in products:
        product: FinishSurface = product
        product.assign_size()
        product.assign_shape()
        print(product.actual_size, product.shape)
        product.save()

@transaction.atomic()
def cluster_sizes(products: QuerySet):
    products.update(size=None)
    sizes = products.filter(actual_size__isnull=False).annotate(
        as_float=Cast('actual_size', output_field=FloatField())
        ).values_list('as_float', flat=True)
    sizes = list(sizes)
    small = np.percentile(sizes, 33)
    medium = np.percentile(sizes, 66)
    print(small, medium)
    small = decimal.Decimal(small)
    medium = decimal.Decimal(medium)
    small = round(small, 2)
    medium = round(medium, 2)

    small_prods = products.filter(actual_size__isnull=False, actual_size__lte=small)
    medium_prods = products.filter(actual_size__isnull=False, actual_size__lte=medium, actual_size__gt=small)
    large_prods = products.filter(actual_size__isnull=False, actual_size__gt=medium)

    sup = str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹')
    unit = ' in2 '.translate(sup)
    o2s = 'small: 0' + unit + ' - ' + str(small) + unit
    s2m = 'medium: ' + str(small) + unit + ' - ' + str(medium) + unit
    m2l = 'large: ' + str(medium) + unit + '+'
    print(o2s, s2m, m2l, medium_prods.count())

    small_prods.update(size='small')
    medium_prods.update(size='medium')
    large_prods.update(size='large')
