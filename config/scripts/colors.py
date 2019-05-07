import webcolors
import scipy
import scipy.cluster
import numpy as np
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

def hex_to_rgb(hex_val):
    hex_val = hex_val.strip('#')
    return tuple(int(hex_val[i:i+2], 16) for i in (0, 2, 4))


def manhattan(x, y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])


def get_rgbs(products: ScraperFinishSurface):
    for product in products:
        product.set_actual_color()
    actual_colors = products.values_list('actual_color', flat=True)
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
    return rgbs


def assign_label_color():
    products = ScraperFinishSurface.objects.using('scraper_revised').all()
    rgbs = get_rgbs(products)
    for product in products:
        if not product.actual_color:
            print('not actual')
            continue
        ac = product.actual_color
        ac = hex_to_rgb(ac)
        distances = {k: manhattan(k, ac) for k in rgbs}
        label_color = min(distances, key=distances.get)
        label_color = webcolors.rgb_to_hex(label_color)
        print(label_color)
        product.label_color = label_color
        product.save()
