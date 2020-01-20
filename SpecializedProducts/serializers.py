from typing import List, Any
from dataclasses import dataclass, asdict
from Products.models import ProductSubClass

@dataclass()
class AdminField:
    term: str = None
    field_type: str = None
    value: Any = None



class AdminFields:

    def __init__(self, product: ProductSubClass):
        # fields = product.get_admin_fields()
        self.admin_fields: List[AdminField] =[]

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
