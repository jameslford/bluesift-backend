"""returns float measurements and labels on product details"""
import io
from typing import List, Any
from dataclasses import dataclass, asdict
import requests
import boto3
import trimesh
from django.db.models import FileField, QuerySet
from django.core.files.base import ContentFile
from django.conf import settings
from Products.models import Product
from Products.models import get_3d_return_path

MATCH_THRESHOLD = .7

class ProductSubClass(Product):
    """returns float measurements and labels on product details"""
    name_fields = []
    admin_fields = []

    class Meta:
        abstract = True

    def grouped_fields(self):
        """returns attribute groups in product detail on front end"""
        return {}

    def geometries(self):
        """returns float measurements and labels on product details"""
        return {}

    def get_width(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_height(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_depth(self):
        """returns float measurements and labels on product details"""
        return 0

    def get_texture_map(self):
        """returns float measurements and labels on product details"""
        return None

    def get_geometry_model(self) -> FileField:
        return None

    def presentation_geometries(self):
        """returns float measurements and labels on product details"""
        # from .serializers import SubproductGeometryPresentationSerializer
        return SubproductGeometryPresentationSerializer(self).data

    def get_admin_fields(self):
        return AdminFields(self).data

    def get_geometry_fields(self):
        return SubproductGeometryPresentationSerializer(self).data

    def import_update(self, **kwargs):
        self.save()

    def import_new(self, **kwargs):
        self.save()

    # def import_match(self, queryset: QuerySet, **kwargs):
    #     values = queryset.values()
    #     matches = []
    #     for prod in values:
    #         score = 0
    #         total = 0
    #         for key, value in kwargs.items():
    #             total += 1
    #             prod_val = prod.get(key)
    #             if prod_val:
    #                 if prod_val == val:
    #                     score += 1
    #                     continue
    #                 score -= 1
    #         percentage = score / total
    #         if percentage >= MATCH_THRESHOLD:
    #             item = [percentage, prod]
    #             matches.append(item)
    #     if not matches()

        # self.save()


    def save_derived_glb(self, mesh: trimesh.Trimesh):
        byteArray = mesh.export(None, 'glb')
        file = ContentFile(byteArray)
        name = str(self.bb_sku) + '.glb'
        self.derived_gbl.save(name, file, save=True)


    @classmethod
    def validate_sub(cls, sub: str):
        """returns float measurements and labels on product details"""
        return bool(sub.lower() in [klas.__name__.lower() for klas in cls.__subclasses__()])

    @classmethod
    def return_sub(cls, sub: str):
        """returns float measurements and labels on product details"""
        classes = [klas for klas in cls.__subclasses__() if klas.__name__.lower() == sub.lower()]
        if classes:
            return classes[0]
        return None


@dataclass()
class AdminField:
    term: str = None
    field_type: str = None
    value: Any = None


class AdminFields:

    def __init__(self, product: ProductSubClass):
        self.admin_fields: List[AdminField] = []

        for field in product.admin_fields:
            value = getattr(product, field)
            model_field = product._meta.get_field(field)
            field_type = model_field.get_internal_type()
            afield = AdminField(term=field, field_type=str(field_type), value=value)
            self.admin_fields.append(afield)

    @property
    def data(self):
        res = [asdict(field) for field in self.admin_fields]
        return res


class SubproductGeometryPresentationSerializer:

    def __init__(self, product: ProductSubClass):
        self.width = product.get_width() if product.get_width() else product.derived_width
        self.depth = product.get_depth() if product.get_depth() else product.derived_depth
        self.height = product.get_height() if product.get_height() else product.derived_height
        self.derived_width = product.derived_width
        self.derived_depth = product.derived_depth
        self.derived_height = product.derived_height
        self.texture_map = product.get_texture_map()

        self.rfa_file = product.rfa_file
        self.ipt_file = product.ipt_file
        self.obj_file = product.obj_file
        # self.rfa_file = product.rfa_file.url if product.rfa_file else None
        # self.ipt_file = product.ipt_file.url if product.ipt_file else None
        # self.obj_file = product.derived_obj.url if product.derived_obj else None
        self.geometry_model = product.derived_gbl.url if product.derived_gbl else None
        self.geometry_clean = product.geometry_clean

    @property
    def data(self):
        return self.__dict__


class Converter:

    def __init__(self, product: ProductSubClass):
        self.product = product
        self.session = {
            'session': boto3.Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
                )
                }

    def get_3d_return_path(self):
        return get_3d_return_path(self.product)

    def download_bytes(self, url: str):
        buffer = io.BytesIO()
        with requests.get(url, stream=True) as req:
            for chunk in req.iter_content(80111, True):
                if chunk:
                    buffer.write(chunk)
        buffer.seek(0)
        req.close()
        return buffer

    def download_string(self, url: str):
        buffer = io.StringIO()
        with requests.get(url, stream=True) as req:
            for chunk in req.iter_content(80111):
                if chunk:
                    chunk.encode('utf-8')
                    buffer.write(chunk)
        req.close()
        return buffer

    def convert(self):
        pass


class Importer:

    def __init__(self):
        self.swatch_image = None
        self.room_scene = None
        self.tiling_image = None

        self.manufacturer_sku = None
        self.manufacturer = None

        super().__init__()

    def add_data(self):
        pass

    def import_data(self, **kwargs):
        pass

    def match_fitness(self):
        pass
