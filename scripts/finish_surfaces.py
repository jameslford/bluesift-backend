import decimal
import io
import webcolors
import scipy
import scipy.cluster
import numpy as np
from PIL import Image, ImageChops
from django.db import transaction
from django.db.models import QuerySet, FloatField
from django.db.models.functions import Cast
from Products.models import ValueCleaner
from SpecializedProducts.models import FinishSurface, Hardwood, Resilient, TileAndStone, LaminateFlooring


# colors = {
#     'red': (255,0,0),
#     'green': (0,255,0),
#     'blue': (0,0,255),
#     'yellow': (255,255,0),
#     'orange': (255,127,0),
#     'white': (255,255,255),
#     'black': (0,0,0),
#     'gray': (127,127,127),
#     'pink': (255,127,127),
#     'purple': (127,0,255),
#           }

colors = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (255, 255, 0),
    (255, 127, 0),
    (255, 255, 255),
    (0, 0, 0),
    (127, 127, 127),
    (255, 127, 127),
    (127, 0, 255)
]

@transaction.atomic
def assign_label_color():
    products = FinishSurface.objects.all()
    rgbs = __get_rgbs(products) + colors
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

def assign_tiling_image(product: FinishSurface):
    # desired_size = settings.DESIRED_IMAGE_SIZE - 2
    if product.tiling_image:
        print('tiling image')
        return
    if not product.swatch_image:
        print('no swatch')
        return
    image: Image.Image = Image.open(product.swatch_image)
    width, height = image.size
    width = width - 2
    height = height - 2
    image = image.convert('RGB')
    tl = image.getpixel((0, 0))
    tr = image.getpixel((width, 0))
    bl = image.getpixel((0, height))
    br = image.getpixel((width, height))
    color_set = set([tl, tr, bl, br])
    if len(color_set) != 1:
        print('not equal')
        return
    new_img = Image.new(image.mode, image.size, tl)
    print(image.size)
    diff: Image.Image = ImageChops.difference(image, new_img)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        tile_image = image.crop(bbox)
        buffer = io.BytesIO()
        try:
            tile_image.save(buffer, 'JPEG', quality=90)
        except IOError:
            print('io error')
            return
        name = 'tiling_' + str(product.bb_sku) + '.jpg'
        product.tiling_image.save(name, buffer, save=True)



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
    # pylint: disable=unsubscriptable-object
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



def __default_clean():
    fs_all = FinishSurface.objects.all()
    for fs in fs_all:
        fs.basic_clean()


def __specific_clean():
    tiles = TileAndStone.objects.all()
    for tile in tiles:
        fin = tile.finish
        if fin:
            split = fin.split(' - ')
            if len(split) > 1:
                new_fin = split[1].strip()
                ValueCleaner.create_or_update(TileAndStone._meta.verbose_name_plural, 'finish', new_fin, fin)
        look = tile.look
        if look:
            if 'mosaic' in look:
                tile.shape = 'mosaic'
                new_look = look.replace('mosaic', '').strip()
                ValueCleaner.create_or_update(TileAndStone._meta.verbose_name_plural, 'look', new_look, look)


def clean_products():
    __default_clean()
    __specific_clean()