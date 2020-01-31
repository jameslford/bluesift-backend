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
        self.derived_width = product.derived_width
        self.derived_depth = product.derived_depth
        self.derived_height = product.derived_height
        self.texture_map = product.get_texture_map()

        self.rfa_file = product.rfa_file.url if product.rfa_file else None
        self.ipt_file = product.ipt_file.url if product.ipt_file else None
        self.obj_file = product.derived_obj.url if product.derived_obj else None
        self.geometry_model = product.derived_gbl.url if product.derived_gbl else None
        self.geometry_clean = product.geometry_clean

    @property
    def data(self):
        return self.__dict__
