from django.core.management.base import BaseCommand
from Products.models import Product
import numpy as np
import scipy
from PIL import Image

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # product = Product.objects.get(id=30)
        # im = product.swatch_image.image
        # im = Image.open(im)
        # # im.show()
        # ar = np.asarray(im)
        # shape = ar.shape
        # ar = ar.reshape(scipy.product(shape[:2]), shape[2]).astype(float)
        # print(ar)
        products = Product.objects.all()
        for product in products:
            if not product.swatch_image:
                product.delete()
