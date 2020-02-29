
from django.db.models import QuerySet
from django.http.request import QueryDict
# from Products.models import Product
from Suppliers.models import SupplierProduct
from .base import BaseReturnValue


class AvailabilityFacet:

    def __init__(self, model_type, location_pk):
        self.name = 'availability'
        self.model_type = model_type
        self.qterms = []
        self.location_pk = location_pk
        self.queryset: QuerySet = None
        self.selected = False
        self.dynamic = True
        self.return_values = []
        self.values = {
            'available_in_store': self.__available_in_store,
            'priced_in_store': self.__priced_in_store,
            'installation_offered': self.__installation_offered
            }
        self._supplier_sets = []

    def __available_in_store(self):
        sps = SupplierProduct.objects.filter(publish_in_store_availability=True).values_list('product__pk', flat=True).distinct()
        self._supplier_sets.append(sps)


    def __priced_in_store(self):
        sps = SupplierProduct.objects.filter(offer_installation=True).values_list('product__pk', flat=True).distinct()
        self._supplier_sets.append(sps)


    def __installation_offered(self):
        sps = SupplierProduct.objects.filter(publish_in_store_price=True).values_list('product__pk', flat=True).distinct()
        self._supplier_sets.append(sps)


    def parse_request(self, params: QueryDict):
        terms = params.getlist(self.name, None)
        terms = terms[0].split(',') if terms else []
        self.qterms = [term for term in terms if term in self.values]
        if self.qterms:
            del params[self.name]
        print(self.qterms)
        return params


    def filter_self(self):
        products = self.model_type.objects.all()
        if not self.qterms:
            self.queryset = products.values_list('pk', flat=True)
            return self.queryset
        for term in self.qterms:
            self.values[term]()
        if self._supplier_sets:
            for pks in self._supplier_sets:
                products = products.filter(pk__in=pks)
            self.queryset = products.values_list('pk', flat=True)
            print(len(self.queryset))
            return self.queryset
        return None

    # pylint: disable=unused-argument
    def count_self(self, query_index_pk, facets, products):
        _facets = [facet.queryset for facet in facets if facet.queryset]
        others = products.intersection(*_facets).values_list('pk', flat=True)
        enabled_values = []
        for value in self.values:
            count = products.filter(pk__in=others).filter_availability(value, self.location_pk).count()
            selected = bool(value in self.qterms)
            expression = f'{self.name}={value}'
            return_value = BaseReturnValue(expression, value, count, selected)
            self.return_values.append(return_value)
            if selected:
                self.selected = True
                enabled_values.append(return_value.asdict())
        return enabled_values

    def serialize_self(self):
        return {
            'name': self.name,
            'selected': self.selected,
            'widget': 'checkbox',
            'editabled': False,
            'exclusive': True,
            'all_values': [value.asdict() for value in self.return_values],
            }
