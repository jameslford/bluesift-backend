from .base import BaseFacet, BaseReturnValue
from django.db import models


class BoolFacet(BaseFacet):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exclusive = True


    def filter_self(self):
        if not self.qterms:
            return None
            # return self.return_stock()
        if self.allow_multiple:
            term = {self.qterms[-1] : True}
            self.queryset = self.model.objects.filter(**term).values_list('pk', flat=True)
            return self.queryset
        terms = {}
        for term in self.qterms:
            terms[term] = True
        if term:
            self.queryset = self.model.objects.filter(**terms).values_list('pk', flat=True)
            return self.queryset
        return None


    def count_self(self, query_index_pk, facets, products=None):
        if not self.dynamic:
            products = self.model.objects.all()
        _facets = [facet.queryset for facet in facets]
        others = self.get_intersection(query_index_pk, products, _facets)
        args = {value: models.Count(value, filter=models.Q(**{value: True})) for value in self.attribute_list}
        bool_values = others.aggregate(**args)
        for name, count in bool_values.items():
            selected = bool(name in self.qterms)
            expression = f'{self.name}={name}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.return_values.append(return_value)
            if selected:
                self.selected = True
                yield return_value.asdict()

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        for attr in self.attribute_list:
            field = self.model._meta.get_field(attr)
            actual_type = field.get_internal_type()
            if self.field_type != field.get_internal_type():
                raise Exception(f'Attribute -{attr}\'s- field type {actual_type} != {self.field_type}')
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
