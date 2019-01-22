from django.core.management.base import BaseCommand
from Products.models import (
    Product,
    Image,
    ShadeVariation,
    SubMaterial,
    Finish,
    Look,
    SurfaceCoating,
    SurfaceTexture
) 


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        Product.objects.all().delete()
        Image.objects.all().delete()
        ShadeVariation.objects.all().delete()
        SubMaterial.objects.all().delete()
        Finish.objects.all().delete()
        Look.objects.all().delete()
        SurfaceCoating.objects.all().delete()
        SurfaceTexture.objects.all().delete()