from .base import ProductSubClass
from django.db import models


class Millwork(ProductSubClass):
    class Meta:
        verbose_name = "millwork"
        verbose_name_plural = "millwork"


class Cabinet(Millwork):
    class Meta:
        verbose_name = "cabinet"
        verbose_name_plural = "cabinets"


class Window(Millwork):
    style = models.CharField(max_length=60, default="casement")
    shape = models.CharField(max_length=60, default="retangular")
    structural_material = models.CharField(max_length=60, default="wood")
    trim_material = models.CharField(max_length=60, null=True, blank=True)
    color = models.CharField(max_length=60, default="white")


class Door(Millwork):
    pass


class Column(Millwork):
    pass
