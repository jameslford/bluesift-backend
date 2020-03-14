from django.db.models import Q, Count
from django.http import QueryDict
from .base import BaseFacet, BaseReturnValue


class ForeignFacet(BaseFacet):

    class Meta:
        proxy = True


    def parse_request(self, params: QueryDict):
        qterms = params.getlist(self.attribute, None)
        self.qterms = qterms[0].split(',') if qterms else []
        return params


    def count_self(self, query_index_pk, facets, products=None):
        _facets = [facet.queryset for facet in facets if facet is not self]
        others = self.get_intersection(query_index_pk, products, _facets)
        name_arg = f'{self.attribute}__label'
        pk_arg = f'{self.attribute}__pk'
        values = others.values(*[name_arg, pk_arg]).annotate(val_count=Count(self.attribute))
        for val in values:
            pk_value = val[pk_arg]
            count = val['val_count']
            selected = bool(str(pk_value) in self.qterms)
            expression = f'{self.attribute}={pk_value}'
            return_value = BaseReturnValue(expression, val[name_arg], count, selected)
            self.return_values.append(return_value)
            if selected:
                self.selected = True
                yield return_value.asdict()


    def filter_self(self):
        if not self.qterms:
            return None
        q_object = Q()
        for term in self.qterms:
            ars = {f'{self.attribute}__pk': int(term)}
            q_object |= Q(**ars)
        self.queryset = self.model.objects.only('pk').filter(q_object).values_list('pk', flat=True)
        return self.queryset
