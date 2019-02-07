from django.core.management.base import BaseCommand
from Products.models import Product, Color
import numpy as np
import scipy
import scipy.cluster
import webcolors


def hex_to_rgb(hex_val):
    hex_val = hex_val.strip('#')
    return tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))


def manhattan(x, y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])


class Command(BaseCommand):

    def handle(self, *args, **options):
        Color.objects.all().delete()
        products = Product.objects.all()
        for product in products:
            if not product.swatch_image:
                product.delete()
                continue
            if not product.swatch_image.image:
                product.delete()
                continue
            product.resize_image()
            product.set_actual_color()
        products = Product.objects.all()
        actual_colors = products.values_list('actual_color__label', flat=True)
        hex_colors = set(actual_colors)
        hex_colors = [z for z in hex_colors if z]
        rgb_colors = [hex_to_rgb(str(q)) for q in hex_colors]
        ar = np.array(rgb_colors)
        shape = ar.shape
        ar = ar.reshape(scipy.product(shape[0]), shape[1]).astype(float)
        codes, dist = scipy.cluster.vq.kmeans(ar, 21, check_finite=False)
        rgbs = []
        for code in codes:
            rounded = tuple(int(round(n)) for n in code)
            rgbs.append(rounded)
        for new_product in products:
            if not new_product.actual_color:
                continue
            ac = new_product.actual_color.label
            ac = hex_to_rgb(ac)
            distances = {k: manhattan(k, ac) for k in rgbs}
            label_color = min(distances, key=distances.get)
            label_color = webcolors.rgb_to_hex(label_color)
            print(label_color)
            label_color, created = Color.objects.get_or_create(label=label_color)
            new_product.label_color = label_color
            new_product.save()

        # print(shape)
