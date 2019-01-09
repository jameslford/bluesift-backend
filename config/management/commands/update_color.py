from django.core.management.base import BaseCommand
from Products.models import Product
from config.management.commands import lists
from PIL import Image, ImageFilter


def manhattan(x, y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])


def get_color2(image):
    image = image.filter(ImageFilter.BoxBlur(10))
    width, height = image.size
    divisor = 4
    left = int(width/divisor)
    right = int(width - width/divisor)
    top = int(height/divisor)
    bottom = int(height - height/divisor)
    im_new = image.convert('RGBA')
    r_total = 0
    g_total = 0
    b_total = 0
    count = 0

    for x in range(left, right):
        for y in range(top, bottom):
            r, g, b, a = im_new.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b
            count += 1

    rgb = (int(round(r_total/count)), int(round(g_total/count)), int(round(b_total/count)))
    distances = {k: manhattan(v, rgb) for k, v in lists.colors.items()}
    color = min(distances, key=distances.get)
    return color


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        products.update(actual_color=None)
        for product in products:
            product.set_actual_color()
            # prod_image = None
            # try:
            #     prod_image = product.swatch_image.image
            # except AttributeError:
            #     continue
            # image = Image.open(prod_image)
            # color2 = get_color2(image)
            # product.actual_color = color2
            # product.save()


# import scipy
# import scipy.cluster
# from django.core.files import File
# import scipy.misc
# import numpy as np
# from django.core.files.uploadedfile import InMemoryUploadedFile


# def get_color(image):
#     NUM_CLUSTERS = 5
#     # im = Image.open(image)
#     im = image
#     im = im.resize((350, 350))      # optional, to reduce time
#     ar = np.asarray(im)
#     shape = ar.shape
#     ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

#     # print('finding clusters')
#     codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
#     # print('cluster centres:\n', codes)

#     vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
#     counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

#     index_max = scipy.argmax(counts)                    # find most frequent
#     peak = codes[index_max]
#     # colour = ''.join(chr(int(c)) for c in peak).encode('hex')
#     colour = ''.join(str(int(c)) for c in peak)
#     colour = str(colour).lstrip('#')
#     # colour = tuple(int(colour[i:i+2], 16) for i in (0, 2, 4))
#     colour = tuple(int(colour[i:i+2], 16) for i in (0, 2, 4))
#     distances = {k: manhattan(v, colour) for k, v in lists.colors.items()}
#     # print(distances)
#     color = min(distances, key=distances.get)
#     return color
    # colour = ''.join(colour)
    # print(colour)
    # print('most frequent is %s (#%s)' % (peak, colour))