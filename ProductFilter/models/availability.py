from django.db.models import QuerySet
from django.http.request import QueryDict
from Products.models import Product
from .base import BaseReturnValue


class AvailabilityFacet:

    def __init__(self, location_pk):
        self.name = 'availability'
        self.qterms = []
        self.location_pk = location_pk
        self.queryset: QuerySet = None
        self.selected = False
        self.dynamic = True
        self.values = Product.objects.safe_availability_commands()
        self.return_values = []

    def parse_request(self, params: QueryDict):
        terms = []
        for key, value in params.items():
            if key == self.name:
                terms.append(value)
        del params[self.name]
        self.qterms = [term for term in terms if term in self.values]
        return params


    def filter_self(self):
        products = Product.objects.all()
        if not self.qterms:
            self.queryset = products.values_list('pk', flat=True)
            return self.queryset
        self.selected = True
        products = products.filter_availability(self.qterms, self.location_pk, True)
        self.queryset = products.values_list('pk', flat=True)
        return self.queryset

    # pylint: disable=unused-argument
    def count_self(self, query_index_pk, products, facets):
        _facets = [facet.queryset for facet in facets if facet.queryset and facet is not self]
        others = products.intersection(*_facets).values_list('pk', flat=True)
        enabled_values = []
        for value in self.values:
            count = products.filter(pk__in=others).filter_availability(value, self.location_pk).count()
            selected = bool(value in self.qterms)
            expression = f'{self.name}={value}'
            return_value = BaseReturnValue(expression, self.name, count, selected)
            self.return_values.append(BaseReturnValue(expression, value, count, selected))
            if selected:
                enabled_values.append(return_value.asdict())
        return enabled_values

    def serialize_self(self):
        return {
            'name': self.name,
            'selected': self.selected,
            'widget': 'checkbox',
            'editabled': False,
            'all_values': [value.asdict() for value in self.return_values],
            }
