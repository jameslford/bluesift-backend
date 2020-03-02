from django.http import QueryDict
from django.contrib.gis.measure import D
from Addresses.models import Zipcode
from Suppliers.models import SupplierLocation
from .base import BaseFacet, BaseReturnValue

class LocationFacet(BaseFacet):

    class Meta:
        proxy = True

    def parse_request(self, params: QueryDict):
        try:
            arg = params.pop('location')
            arg = arg[0].split(',')
            self.zipcode, self.radius = arg[-1].split('*')
            return params
        except (KeyError, IndexError):
            return params


    def filter_self(self):
        if not (self.radius and self.zipcode):
            return None
        try:
            radius = D(mi=int(self.radius))
        except ValueError:
            self.radius = None
            return None
        coords = Zipcode.objects.filter(code=self.zipcode).first()
        if not coords:
            return None
        self.selected = True
        expression = f'location={self.zipcode}*{self.radius}'
        name = f'Within {self.radius} mi.'
        self.enabled_values.append(BaseReturnValue(expression, name, None, True).asdict())
        locs = SupplierLocation.objects.filter(address__coordinates__point__distance_lte=(
            coords.centroid.point, radius
            ))
        self.queryset = locs.values_list('products__product__pk', flat=True).distinct()

        return self.queryset

    def count_self(self, query_index_pk, facets, products=None):
        return self.enabled_values

    def serialize_self(self):
        return_dict = super().serialize_self()
        return_dict.update({'radii': [5, 10, 25, 50, 100, 200]})
        return_dict.update({'zipcode': self.zipcode})
        return_dict.update({'radius': self.radius})
        return return_dict
