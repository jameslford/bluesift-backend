import decimal
import webcolors
import scipy
import scipy.cluster
import numpy as np
from django.db import transaction
from django.db.models import QuerySet, FloatField
from django.db.models.functions import Cast
from SpecializedProducts.models import FinishSurface

@transaction.atomic
def assign_label_color():
    products = FinishSurface.objects.all()
    rgbs = __get_rgbs(products)
    for product in products:
        if not product.actual_color:
            print('not actual')
            continue
        ac = product.actual_color
        ac = __hex_to_rgb(ac)
        distances = {k: __manhattan(k, ac) for k in rgbs}
        label_color = min(distances, key=distances.get)
        label_color = webcolors.rgb_to_hex(label_color)
        print(label_color)
        product.label_color = label_color
        product.save()


@transaction.atomic
def assign_size():
    products = FinishSurface.subclasses.all().select_subclasses()
    __set_size(products)
    __cluster_sizes(products)


def __hex_to_rgb(hex_val):
    hex_val = hex_val.strip('#')
    return tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))


def __manhattan(x, y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])


def __get_rgbs(products: FinishSurface):
    for product in products:
        product.set_actual_color()
    actual_colors = products.values_list('actual_color', flat=True)
    hex_colors = set(actual_colors)
    hex_colors = [z for z in hex_colors if z]
    rgb_colors = [__hex_to_rgb(str(q)) for q in hex_colors]
    ar = np.array(rgb_colors)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[0]), shape[1]).astype(float)
    codes, dist = scipy.cluster.vq.kmeans(ar, 19, check_finite=False)
    rgbs = []
    for code in codes:
        rounded = tuple(int(round(n)) for n in code)
        rgbs.append(rounded)
    return rgbs


def __set_size(products: QuerySet):
    for product in products:
        product: FinishSurface = product
        product.assign_size()
        print(product.actual_size)
        product.save()


def __cluster_sizes(products: QuerySet):
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
