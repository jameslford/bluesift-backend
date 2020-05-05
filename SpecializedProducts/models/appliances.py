import io
import zipfile
import decimal
import tempfile
import requests
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.fields import DecimalRangeField
from django.contrib.contenttypes.models import ContentType
import trimesh
from trimesh.visual.resolvers import WebResolver
from Products.models import Manufacturer
from ProductFilter.models import BaseFacet
from .base import Converter, ProductSubClass


class ApplianceColor(models.Model):
    hex_value = models.CharField(max_length=10)
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(
        Manufacturer, on_delete=models.SET_NULL, null=True, blank=True
    )


class Appliance(ProductSubClass):
    inches = "inches"
    cm = "centimeter"
    mm = "millimeter"
    ft = "feet"
    unit_choices = [inches, cm, mm, ft]
    appliance_type = models.CharField(max_length=100, blank=True, null=True)
    room_type = models.CharField(max_length=100, null=True, blank=True)
    finishes = ArrayField(
        models.CharField(max_length=70, null=True), null=True, blank=True
    )
    colors = models.ManyToManyField(ApplianceColor)
    width = DecimalRangeField(null=True, blank=True)
    height = DecimalRangeField(null=True, blank=True)
    depth = DecimalRangeField(null=True, blank=True)

    def assign_name(self):
        if self.name:
            return self.name
        self.name = f"{self.manufacturer.label}, {self.manufacturer_collection}, {self.manufacturer_style}".lower()
        self.save()
        return self.name

    def get_height(self):
        # pylint:disable = no-member
        return float(self.height.lower) if self.height and self.height.lower else None

    def get_width(self):
        # pylint:disable = no-member
        return float(self.width.lower) if self.width and self.width.lower else None

    def get_depth(self):
        # pylint:disable = no-member
        return float(self.depth.lower) if self.depth and self.depth.lower else None

    def add_proprietary_files(self):
        converter = ApplianceConverter(self)
        converter.add_proprietary_files()

    def convert_geometries(self):
        converter = ApplianceConverter(self)
        converter.convert()

    def grouped_fields(self):
        return {
            "size_and_shaped": {
                "height": self.get_height(),
                "width": self.get_width(),
                "depth": self.get_depth(),
            },
        }

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if not self.height:
            self.height = (self.derived_height, None)
        if not self.width:
            self.width = (self.derived_width, None)
        if not self.depth:
            self.depth = (self.derived_depth, None)
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    @classmethod
    def create_facets(cls):
        capp = ContentType.objects.get_for_model(Appliance)
        BaseFacet.objects.get_or_create(
            content_type=capp,
            attribute="derived_width",
            field_type="DecimalField",
            widget="slider",
            name="width",
        )
        BaseFacet.objects.get_or_create(
            content_type=capp,
            attribute="derived_depth",
            field_type="DecimalField",
            widget="slider",
            name="depth",
        )
        BaseFacet.objects.get_or_create(
            content_type=capp,
            attribute="derived_height",
            field_type="DecimalField",
            name="height",
            widget="slider",
        )


class ApplianceConverter(Converter):
    def __init__(self, product):
        self.resolver = None
        super().__init__(product)

    def create_derived_obj(self):
        with self.product._obj_file.open("r") as data:
            buffer = io.StringIO()
            for line in data.readlines():
                line = line.decode()
                if "mtllib" in line:
                    print(line)
                    new_line = "mtllib " + self.product._mtl_file.url
                    buffer.write(new_line)
                else:
                    buffer.write(line)
            buffer.seek(0)
            for line in buffer.readlines():
                if "mtllib" in line:
                    print(line)
            buffer.seek(0)
            self.resolver = WebResolver
            return buffer

    def get_initial(self) -> io.BytesIO:
        if not self.product._obj_file:
            return None
        if self.product._mtl_file:
            print(self.product.name, "has mtlf")
            return self.create_derived_obj()
        print(self.product.name, "no mtl file")
        res = self.download_bytes(self.product._obj_file.url)
        return res

    def add_proprietary_files(self):
        product = self.product
        prop_array = [
            [".rfa", product.rfa_file, product._rfa_file],
            ["_2d.dwg", product.dwg_2d_file, product._dwg_2d_file],
            ["_3d.dwg", product.dwg_3d_file, product._dwg_3d_file],
            [".dxf", product.dxf_file, product._dxf_file],
        ]
        for ext, origin, destination in prop_array:
            print(ext, origin, destination)
            if not origin or origin == "None":
                continue
            if destination:
                continue
            request = requests.get(origin, stream=True)
            # pylint: disable=no-member
            if request.status_code != requests.codes.ok:
                continue
            filename = str(product.pk) + ext
            lf = tempfile.NamedTemporaryFile()
            for block in request.iter_content(1024 * 8):
                if not block:
                    break
                lf.write(block)
            destination.save(filename, lf, save=True)

    def convert(self):
        if not self.product.obj_file:
            return
        try:
            mes: trimesh.Trimesh = trimesh.load_remote(self.product.obj_file)
        except zipfile.BadZipFile:
            self.product.delete()
            return
        conversion_unit = self.product.cm
        if conversion_unit != self.product.inches:
            mes.units = conversion_unit
            mes = mes.convert_units("inches", True)
        self.assign_sizes(mes)
        self.product.save_derived_glb(mes)
        self.add_proprietary_files()

    def assign_sizes(self, mes: trimesh.Trimesh):
        length, height, depth = mes.extents
        center = mes.centroid
        print(center.tolist(), type(center))
        length = decimal.Decimal(round(length, 2))
        depth = decimal.Decimal(round(depth, 2))
        height = decimal.Decimal(round(height, 2))
        self.product.derived_center = center.tolist()
        self.product.derived_depth = depth
        self.product.derived_height = height
        self.product.derived_width = length


class Cooking(Appliance):
    fuel_type = models.CharField(max_length=20, null=True, blank=True)

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("room_type", "kitchen")
        super(Cooking, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name_plural = "cooking"


class Range(Cooking):
    burner_count = models.IntegerField(null=True, blank=True)


class Oven(Cooking):
    pass


class Microwave(Cooking):
    pass


class Refrigeration(Appliance):
    class Meta:
        verbose_name_plural = "refrigeration"
