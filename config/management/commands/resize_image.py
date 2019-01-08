from django.core.management.base import BaseCommand
# from django.core.files.uploadedfile import InMemoryUploadedFile
# from django.core.files import File
from Products.models import Product
# from config.management.commands import lists
# from PIL import Image, ImageFilter
# import scipy
# import scipy.cluster
# import scipy.misc
# import numpy as np
# import io


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        products = Product.objects.all()
        for product in products:
            product.resize_image()


# def resize_image(image, product):
#     buffer = io.BytesIO()
#     # image = image.filter(ImageFilter.BoxBlur(100))
#     w, h = image.size
#     desired_size = 350
#     w_ratio = desired_size/w
#     height_adjust = int(round(h * w_ratio))
#     image = image.resize((desired_size, height_adjust))
#     image = image.crop((
#         0,
#         0,
#         desired_size,
#         desired_size
#         ))
#     image.save(buffer, 'JPEG')
#     image_name = product.name.replace(' ', '') + 'tiling_image.jpg'
#     django_image = ProdImage()
#     django_image.original_url = image_name
#     tile_image.image.save(image_name, buffer)
#     tile_image.save()
#     product.tiling_image = tile_image
#     print(product.tiling_image.original_url, product.id)
#     return product