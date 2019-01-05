from django.core.management.base import BaseCommand, CommandError
from Products.models import Product
from PIL import Image, ImageFilter
import scipy
import scipy.cluster
import scipy.misc
import numpy as np


colorse = {
    'Black': (0, 0, 0),
    'White': (255, 255, 255),
    'Red': (255, 0, 0),
    'Lime': (0, 255, 0),
    'Blue': (0, 0, 255),
    'Yellow': (255, 255, 0),
    'Cyan': (0, 255, 255),
    'Magenta': (255, 0, 255),
    'Silver': (192, 192, 192),
    'Gray': (128, 128, 128),
    'Maroon': (128, 0, 0),
    'Orange': (255, 165, 0),
    'Olive': (128, 128, 0),
    'Green': (0, 128, 0),
    'Purple': (128, 0, 128),
    'Teal': (0, 128, 128),
    'Navy': (0, 0, 128),
    'cornsilk': (255, 248, 220),
    'blanchedalmond': (255, 235, 205),
    'bisque': (255, 228, 196),
    'navajowhite': (255, 222, 173),
    'wheat': (245, 222, 179),
    'burlywood': (222, 184, 135),
    'tan': (210, 180, 140),
    'rosybrown': (188, 143, 143),
    'sandybrown': (244, 164, 96),
    'goldenrod': (218, 165, 32),
    'peru': (205, 133, 63),
    'chocolate': (210, 105, 30),
    'saddlebrown': (139, 69, 19),
    'sienna': (160, 82, 45),
    'brown': (165, 42, 42),
    'maroon': (128, 0, 0)
}

colors = {
    'maroon': (128, 0, 0),
    'dark_red': (139, 0, 0),
    'brown': (165, 42, 42),
    'firebrick': (178, 34, 34),
    'crimson': (220, 20, 60),
    'red': (255, 0, 0),
    'tomato': (255, 99, 71),
    'coral': (255, 127, 80),
    'indian_red': (205, 92, 92),
    'light_coral': (240, 128, 128),
    'dark_salmon': (233, 150, 122),
    'salmon': (250, 128, 114),
    'light_salmon': (255, 160, 122),
    'orange_red': (255, 69, 0),
    'dark_orange': (255, 140, 0),
    'orange': (255, 165, 0),
    'gold': (255, 215, 0),
    'dark_goldenrod': (184, 134, 11),
    'golden_rod': (218, 165, 32),
    'pale_goldenrod': (238, 232, 170),
    'dark_khaki': (189, 183, 107),
    'khaki': (240, 230, 140),
    'olive': (128, 128, 0),
    'yellow': (255, 255, 0),
    'yellow_green': (154, 205, 50),
    'dark_olive_green': (85, 107, 47),
    'olive_drab': (107, 142, 35),
    'lawn_green': (124, 252, 0),
    'chart_reuse': (127, 255, 0),
    'green_yellow': (173, 255, 47),
    'dark_green': (0, 100, 0),
    'green': (0, 128, 0),
    'forest_green': (34, 139, 34),
    'lime': (0, 255, 0),
    'lime_green': (50, 205, 50),
    'light_green': (144, 238, 144),
    'pale_green': (152, 251, 152),
    'dark_sea_green': (143, 188, 143),
    'medium_spring_green': (0, 250, 154),
    'spring_green': (0, 255, 127),
    'sea_green': (46, 139, 87),
    'medium_aqua_marine': (102, 205, 170),
    'medium_sea_green': (60, 179, 113),
    'light_sea_green': (32, 178, 170),
    'dark_slate_gray': (47, 79, 79),
    'teal': (0, 128, 128),
    'dark_cyan': (0, 139, 139),
    'aqua': (0, 255, 255),
    'cyan': (0, 255, 255),
    'light_cyan': (224, 255, 255),
    'dark_turquoise': (0, 206, 209),
    'turquoise': (64, 224, 208),
    'medium_turquoise': (72, 209, 204),
    'pale_turquoise': (175, 238, 238),
    'aqua_marine': (127, 255, 212),
    'powder_blue': (176, 224, 230),
    'cadet_blue': (95, 158, 160),
    'steel_blue': (70, 130, 180),
    'corn_flower_blue': (100, 149, 237),
    'deep_sky_blue': (0, 191, 255),
    'dodger_blue': (30, 144, 255),
    'light_blue': (173, 216, 230),
    'sky_blue': (135, 206, 235),
    'light_sky_blue': (135, 206, 250),
    'midnight_blue': (25, 25, 112),
    'navy': (0, 0, 128),
    'dark_blue': (0, 0, 139),
    'medium_blue': (0, 0, 205),
    'blue': (0, 0, 255),
    'royal_blue': (65, 105, 225),
    'blue_violet': (138, 43, 226),
    'indigo': (75, 0, 130),
    'dark_slate_blue': (72, 61, 139),
    'slate_blue': (106, 90, 205),
    'medium_slate_blue': (123, 104, 238),
    'medium_purple': (147, 112, 219),
    'dark_magenta': (139, 0, 139),
    'dark_violet': (148, 0, 211),
    'dark_orchid': (153, 50, 204),
    'medium_orchid': (186, 85, 211),
    'purple': (128, 0, 128),
    'thistle': (216, 191, 216),
    'plum': (221, 160, 221),
    'violet': (238, 130, 238),
    'magenta': (255, 0, 255),
    'orchid': (218, 112, 214),
    'medium_violet_red': (199, 21, 133),
    'pale_violet_red': (219, 112, 147),
    'deep_pink': (255, 20, 147),
    'hot_pink': (255, 105, 180),
    'light_pink': (255, 182, 193),
    'pink': (255, 192, 203),
    'antique_white': (250, 235, 215),
    'beige': (245, 245, 220),
    'bisque': (255, 228, 196),
    'blanched_almond': (255, 235, 205),
    'wheat': (245, 222, 179),
    'corn_silk': (255, 248, 220),
    'lemon_chiffon': (255, 250, 205),
    'light_goldenrod': (250, 250, 210),
    'light_yellow': (255, 255, 224),
    'saddle_brown': (139, 69, 19),
    'sienna': (160, 82, 45),
    'chocolate': (210, 105, 30),
    'peru': (205, 133, 63),
    'sandy_brown': (244, 164, 96),
    'burly_wood': (222, 184, 135),
    'tan': (210, 180, 140),
    'rosy_brown': (188, 143, 143),
    'moccasin': (255, 228, 181),
    'navajo_white': (255, 222, 173),
    'peach_puff': (255, 218, 185),
    'misty_rose': (255, 228, 225),
    'lavender_blush': (255, 240, 245),
    'linen': (250, 240, 230),
    'old_lace': (253, 245, 230),
    'papaya_whip': (255, 239, 213),
    'sea_shell': (255, 245, 238),
    'mint_cream': (245, 255, 250),
    'slate_gray': (112, 128, 144),
    'light_slate_gray': (119, 136, 153),
    'light_steel_blue': (176, 196, 222),
    'lavender': (230, 230, 250),
    'floral_white': (255, 250, 240),
    'alice_blue': (240, 248, 255),
    'ghost_white': (248, 248, 255),
    'honeydew': (240, 255, 240),
    'ivory': (255, 255, 240),
    'azure': (240, 255, 255),
    'snow': (255, 250, 250),
    'black': (0, 0, 0),
    'dim_gray': (105, 105, 105),
    'gray': (128, 128, 128),
    'dark_gray': (169, 169, 169),
    'silver': (192, 192, 192),
    'light_gray': (211, 211, 211),
    'gainsboro': (220, 220, 220),
    'white_smoke': (245, 245, 245),
    'white': (255, 255, 255)
}


def manhattan(x, y):
    return abs(x[0] - y[0]) + abs(x[1] - y[1]) + abs(x[2] - y[2])


def get_color(image):
    NUM_CLUSTERS = 5
    # im = Image.open(image)
    im = image
    im = im.resize((350, 350))      # optional, to reduce time
    ar = np.asarray(im)
    shape = ar.shape
    ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)

    # print('finding clusters')
    codes, dist = scipy.cluster.vq.kmeans(ar, NUM_CLUSTERS)
    # print('cluster centres:\n', codes)

    vecs, dist = scipy.cluster.vq.vq(ar, codes)         # assign codes
    counts, bins = scipy.histogram(vecs, len(codes))    # count occurrences

    index_max = scipy.argmax(counts)                    # find most frequent
    peak = codes[index_max]
    # colour = ''.join(chr(int(c)) for c in peak).encode('hex')
    colour = ''.join(str(int(c)) for c in peak)
    colour = str(colour).lstrip('#')
    # colour = tuple(int(colour[i:i+2], 16) for i in (0, 2, 4))
    colour = tuple(int(colour[i:i+2], 16) for i in (0, 2, 4))
    distances = {k: manhattan(v, colour) for k, v in colors.items()}
    # print(distances)
    color = min(distances, key=distances.get)
    return color
    # colour = ''.join(colour)
    # print(colour)
    # print('most frequent is %s (#%s)' % (peak, colour))




def get_color2(image):
    # image = image.resize((350, 350))
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
            new_x = float(x)
            new_y = float(y)
            r, g, b, a = im_new.getpixel((x, y))
            r_total += r
            g_total += g
            b_total += b
            count += 1

    rgb = (int(round(r_total/count)), int(round(g_total/count)), int(round(b_total/count)))
    distances = {k: manhattan(v, rgb) for k, v in colors.items()}
    color = min(distances, key=distances.get)
    # print(distances)
    return color

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        products.update(actual_color=None)
        for product in products:
            prod_image = None
            try:
                prod_image = product.swatch_image.image
            except AttributeError:
                continue
            image = Image.open(prod_image)
            # color = get_color(image)
            # print(color)
            color2 = get_color2(image)
            # print(color2)
            # print('------')
            # for x, y in zip(color, color2):
            #     print(x, y)

            product.actual_color = color2
            product.save()
            print(color2)

