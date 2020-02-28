from .base import BaseFacet, BaseReturnValue
from django.db.models import Q, Count



class CharFacet(BaseFacet):

    class Meta:
        proxy = True

    def count_self(self, query_index_pk, products, facets):
        _facets = [facet.queryset for facet in facets if facet is not self]
        others = self.get_intersection(query_index_pk, products, _facets)
        values = others.values(self.attribute).annotate(val_count=Count(self.attribute))
        for val in values:
            count = val['val_count']
            if not count:
                continue
            name = val[self.attribute]
            selected = bool(name in self.qterms)
            expression = f'{self.name}={name}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.return_values.append(return_value)
            if self.name == 'color':
                return_value.color = True
            if selected:
                yield return_value.asdict()

    def filter_self(self):
        if not self.qterms:
            return self.return_stock()
        q_object = Q()
        if not isinstance(self.qterms, list):
            return None
        for term in self.qterms:
            q_object |= Q(**{self.attribute: term})
            self.selected = True
        self.queryset = self.model.objects.filter(q_object).values_list('pk', flat=True)
        return self.queryset
