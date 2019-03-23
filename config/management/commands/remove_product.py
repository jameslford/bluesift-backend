from django.core.management.base import BaseCommand
from Products.models import (
    Product,
    Image,
    Manufacturer
)
from FinishSurfaces.models import (
    FinishSurface,
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
        Manufacturer.objects.all().delete()
        ShadeVariation.objects.all().delete()
        SubMaterial.objects.all().delete()
        Finish.objects.all().delete()
        Look.objects.all().delete()
        SurfaceCoating.objects.all().delete()
        SurfaceTexture.objects.all().delete()
        FinishSurface.objects.all().delete()
