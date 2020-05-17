from .base import ProductSubClass


class Millwork(ProductSubClass):
    class Meta:
        verbose_name = "millwork"
        verbose_name_plural = "millwork"


class Cabinet(Millwork):
    class Meta:
        verbose_name = "cabinet"
        verbose_name_plural = "cabinets"


class Window(Millwork):
    pass


class Door(Millwork):
    pass


class Column(Millwork):
    pass
