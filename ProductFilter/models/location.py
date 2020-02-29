from django.http import QueryDict
from django.contrib.gis.measure import D
from Addresses.models import Zipcode
from Products.models import Product
from .base import BaseFacet, BaseReturnValue





class LocationFacet(BaseFacet):

    class Meta:
        proxy = True


    def parse_request(self, params: QueryDict):
        try:
            arg = params.pop('radius')
            self.radius, self.zipcode = arg.split('*')
            return params
        except (KeyError, IndexError):
            return params


    def filter_self(self):
        if not (self.radius and self.zipcode):
            return self.return_stock()
        try:
            radius = D(mi=int(self.radius))
        except ValueError:
            self.radius = None
            return None
            # return self.return_stock()
        coords = Zipcode.objects.filter(code=self.zipcode).first().centroid.point
        if not coords:
            return None
            # return self.return_stock()
        self.selected = True
        expression = f'radius={self.radius}*{self.zipcode}'
        name = f'Within {self.radius} mi.'
        self.enabled_values.append(BaseReturnValue(expression, name, None, True).asdict())
        prods = Product.objects.filter(locations__distance_lte=(coords, radius))
        self.queryset = prods.values_list('pk', flat=True)
        return self.queryset


    def serialize_self(self):
        return_dict = super().serialize_self()
        return_dict.update({'radii': [5, 10, 25, 50, 100, 200]})
        return_dict.update({'zipcode': self.zipcode})
        return_dict.update({'radius': self.radius})
