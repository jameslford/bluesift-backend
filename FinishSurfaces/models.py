import operator
import webcolors
from PIL import Image as pimage
from django.db import models
from Products.models import ProductSubClass


class FinishSurface(ProductSubClass):

    label_color = models.CharField(max_length=50, null=True, blank=True)
    actual_color = models.CharField(max_length=50, null=True, blank=True)

    material = models.CharField(max_length=200)
    sub_material = models.CharField(max_length=200, null=True, blank=True)

    finish = models.CharField(max_length=200, null=True, blank=True)
    surface_coating = models.CharField(max_length=200, null=True, blank=True)
    look = models.CharField(max_length=200, null=True, blank=True)
    shade_variation = models.CharField(max_length=200, null=True, blank=True)

    walls = models.BooleanField(default=False)
    countertops = models.BooleanField(default=False)
    floors = models.BooleanField(default=False)
    cabinet_fronts = models.BooleanField(default=False)
    shower_floors = models.BooleanField(default=False)
    shower_walls = models.BooleanField(default=False)
    exterior_walls = models.BooleanField(default=False)
    exterior_floors = models.BooleanField(default=False)
    covered_walls = models.BooleanField(default=False)
    covered_floors = models.BooleanField(default=False)
    pool_linings = models.BooleanField(default=False)
    bullnose = models.BooleanField(default=False)
    covebase = models.BooleanField(default=False)
    corner_covebase = models.BooleanField(default=False)

    thickness = models.DecimalField(max_digits=6, decimal_places=3, null=True)
    width = models.CharField(max_length=50, null=True, blank=True)
    length = models.CharField(max_length=50, null=True, blank=True)

    size = models.CharField(max_length=80, null=True, blank=True)
    shape = models.CharField(max_length=80, null=True, blank=True)

    lrv = models.CharField(max_length=60, null=True, blank=True)
    cof = models.CharField(max_length=60, null=True)

    edge = models.CharField(max_length=200, null=True, blank=True)
    end = models.CharField(max_length=200, null=True, blank=True)
    install_type = models.CharField(max_length=100, null=True)

    sqft_per_carton = models.CharField(max_length=70, null=True)
    slip_resistant = models.BooleanField(default=False)


    def set_size(self):
        if not self.size:
            self.size = self.width + ' x ' + self.length

    @classmethod
    def special_method(cls):
        print('hello world')


    def set_actual_color(self):
        # pylint: disable=no-member
        image = self.swatch_image
        if not image:
            return
        try:
            image = pimage.open(image)
        except OSError:
            print('deleting ' + self.name + 'from set_actual_color')
            self.delete()
            return
        try:
            image = image.convert('P', palette=pimage.ADAPTIVE, colors=1)
        except ValueError:
            print('unable')
            return
        image = image.convert('RGB')

        colors = image.getcolors()
        first_percentage, first_color = max(colors, key=operator.itemgetter(0))
        real_color = webcolors.rgb_to_hex(first_color)
        self.actual_color = real_color
        self.save()


