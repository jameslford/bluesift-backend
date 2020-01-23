from typing import List, Any
from dataclasses import dataclass, asdict
from .models import ProductSubClass


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


class SubproductGeometryConversionSerializer:

    def __init__(self, product: ProductSubClass):
        self.width = product.get_width()
        self.depth = product.get_depth()
        self.height = product.get_height()
        self.texture_map = product.get_texture_map()
        self.obj_file = product.obj_file.url if product.obj_file else None
        self.mtl_file = product.mtl_file.url if product.mtl_file else None
        self.gltf_file = product.gltf_file.url if product.gltf_file else None
        self.stl_file = product.stl_file.url if product.stl_file else None
        self.dae_file = product.dae_file.url if product.dae_file else None
        self.three_json = product.three_json
        self.geometry_clean = product.geometry_clean

    @property
    def data(self):
        return self.__dict__


class SubproductGeometryPresentationSerializer:

    def __init__(self, product: ProductSubClass):
        self.width = product.get_width() if product.get_width() else product.derived_width
        self.depth = product.get_depth()
        self.height = product.get_height()
        self.texture_map = product.get_texture_map()
        self.obj_file = product.obj_file.url if product.obj_file else None
        self.mtl_file = product.mtl_file.url if product.mtl_file else None
        self.gltf_file = product.gltf_file.url if product.gltf_file else None
        self.stl_file = product.stl_file.url if product.stl_file else None
        self.dae_file = product.dae_file.url if product.dae_file else None
        self.three_json = product.three_json
        self.geometry_clean = product.geometry_clean

    @property
    def data(self):
        return self.__dict__
