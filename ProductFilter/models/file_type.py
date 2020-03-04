from django.db.models import Q
from django.db import models
from .base import BaseFacet, BaseReturnValue



class FileTypeFacet(BaseFacet):

    class Meta:
        proxy = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.exclusive = True


    def filter_self(self):
        if not self.qterms:
            return None
        q_object = Q()
        if not isinstance(self.qterms, list):
            return None
        for term in self.qterms:
            arg = {f'{term}': ''}
            q_object &= ~Q(**arg)
            self.selected = True
        self.queryset = self.model.objects.only('pk').filter(q_object).values_list('pk', flat=True)
        return self.queryset


    def count_self(self, query_index_pk, facets, products):
        _facets = [facet.queryset for facet in facets]
        others = self.get_intersection(query_index_pk, products, _facets)
        args = {value: models.Count(value, filter=(~models.Q(**{value: ''}))) for value in self.attribute_list}
        bool_values = others.aggregate(**args)
        for name, count in bool_values.items():
            selected = bool(name in self.qterms)
            expression = f'{self.name}={name}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.return_values.append(return_value)
            if selected:
                self.selected = True
                yield return_value.asdict()
