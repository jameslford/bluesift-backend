from typing import List
from Suppliers.models import SupplierLocation

class Tree:

    def __init__(self, name, count):
        self.name = name
        self.count = count
        self.children: List[Tree] = []
        # self.name = cls._meta.verbose_name_plural.lower().strip()
        # self.count = cls.objects.count()

    def serialize(self):
        return {
            'name': self.name,
            'count': self.count,
            'children': [child.serialize() for child in self.children]
            }
 
    @classmethod
    def loop_product(cls, current: object, parent):
        if not current._meta.abstract:
            name = current._meta.verbose_name_plural.lower().strip()
            count = current.objects.count()
            new_tree = cls(name, count)
            parent.children.append(new_tree)
            for sub in current.__subclasses__():
                cls.loop_product(sub, new_tree)
        else:
            for child in current.__subclasses__():
                cls.loop_product(child, parent)

    @classmethod
    def loop_supplier(cls, current: object, parent):
        if not current._meta.abstract:
            name = current._meta.verbose_name_plural.lower().strip()
            supplier_product_pks = current.objects.values('priced__location__pk').distinct()
            count = SupplierLocation.objects.filter(pk__in=supplier_product_pks).count()
            new_tree = cls(name, count)
            parent.children.append(new_tree)
            for sub in current.__subclasses__():
                cls.loop_product(sub, new_tree)
        else:
            for child in current.__subclasses__():
                cls.loop_product(child, parent)
