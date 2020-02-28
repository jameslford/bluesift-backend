from django.db.models import Q, Count
from django.http import QueryDict
from .base import BaseFacet, BaseReturnValue




class ForeignFacet(BaseFacet):

    class Meta:
        proxy = True


    def count_self(self, query_index_pk, products, facets):
        _facets = [facet.queryset for facet in facets if facet is not self]
        others = self.get_intersection(query_index_pk, products, _facets)
        name_arg = f'{self.attribute}__label'
        pk_arg = f'{self.attribute}__pk'
        values = others.values(*[name_arg, pk_arg]).annotate(val_count=Count(self.attribute))
        for val in values:
            name = val[name_arg]
            pk_value = val[pk_arg]
            count = val['val_count']
            selected = bool(str(pk_value) in self.qterms)
            expression = f'{self.name}={pk_value}'
            return_value = BaseReturnValue(expression, name, count, selected)
            self.return_values.append(return_value)
            if selected:
                yield return_value.asdict()


    def filter_self(self):
        print(self.qterms)
        if not self.qterms:
            return self.return_stock()
        q_object = Q()
        for term in self.qterms:
            ars = {f'{self.attribute}__pk': int(term)}
            q_object |= Q(**ars)
            self.selected = True
        self.queryset = self.model.objects.filter(q_object).values_list('pk', flat=True)
        return self.queryset
