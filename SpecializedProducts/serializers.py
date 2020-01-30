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



class SubproductGeometryPresentationSerializer:

    def __init__(self, product: ProductSubClass):
        self.width = product.get_width() if product.get_width() else product.derived_width
        self.depth = product.get_depth() if product.get_depth() else product.derived_depth
        self.height = product.get_height() if product.get_height() else product.derived_height
        self.texture_map = product.get_texture_map()
        self.obj_file = product.get_obj_file()
        self.mtl_file = product.get_mtl_file()
        self.gltf_file = product.get_gltf_file()
        self.stl_file = product.get_stl_file()
        self.dae_file = product.get_dae_file()
        self.rfa_file = product.rfa_file.url if product.rfa_file else None
        self.ipt_file = product.ipt_file.url if product.ipt_file else None
        self.geometry_model = product.get_geometry_model()
        self.three_json = product.three_json
        self.geometry_clean = product.geometry_clean

    @property
    def data(self):
        return self.__dict__
