
from typing import Set
from django.db.models import QuerySet, Q
from django.http.request import QueryDict
from Products.models import Product
from Suppliers.models import SupplierProduct
from .base import BaseReturnValue


class AvailabilityFacet:

    def __init__(self, location_pk):
        self.name = 'availability'

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
        # sps = SupplierProduct.objects.filter(publish_in_store_availability=True)

        # if self._supplier_sets:
        #     self._supplier_sets = self._supplier_sets.intersection(sps)
        # else:
        #     self._supplier_sets = set(sps)

    def __priced_in_store(self):
        sps = SupplierProduct.objects.filter(offer_installation=True).values_list('product__pk', flat=True).distinct()
        self._supplier_sets.append(sps)

        # if self._supplier_sets:
        #     self._supplier_sets = self._supplier_sets.intersection(sps)
        # else:
        #     self._supplier_sets = set(sps)

    def __installation_offered(self):
        sps = SupplierProduct.objects.filter(publish_in_store_price=True).values_list('product__pk', flat=True).distinct()
        self._supplier_sets.append(sps)
        # if self._supplier_sets:
        #     self._supplier_sets = self._supplier_sets.intersection(sps)
        # else:
        #     self._supplier_sets = set(sps)



    def parse_request(self, params: QueryDict):
        terms = params.getlist(self.name, None)
        terms = terms[0].split(',') if terms else []
        self.qterms = [term for term in terms if term in self.values]

        # for key, values in params.items():
        #     print(key, values)
        #     if key == self.name:
        #         for value in values
        #         self.selected = True
        #         terms.append(value)
        if self.qterms:
            del params[self.name]
        print(self.qterms)
        return params


    def filter_self(self):
        products = Product.objects.all()
        if not self.qterms:
            self.queryset = products.values_list('pk', flat=True)
            return self.queryset
        for term in self.qterms:
            self.values[term]()
        if self._supplier_sets:
            q_object = Q()
            for pks in self._supplier_sets:
                products = products.filter(pk__in=pks)
                # ars = {'pk__in': pks}
                # q_object |= Q(**ars)
            self.queryset = products.values_list('pk', flat=True)
            print(len(self.queryset))
            return self.queryset
        return None


        # self.selected = True
        # products = products.filter_availability(self.qterms, self.location_pk, True)
        # self.queryset = products.values_list('pk', flat=True)
        # return self.queryset

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
