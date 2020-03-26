import decimal
from django.db.models import Min, Max, QuerySet
from django.http import QueryDict
from Products.models import Product
from .base import BaseReturnValue


class PriceFacet:

    def __init__(self, location_pk):
        self.name = 'price'
        self.qterms = []
        self.location_pk = location_pk
        self.queryset: QuerySet = None
        self.selected = False
        self.dynamic = True
        self.attribute = 'low_price'
        self.return_values = []
        self.abs_max = None
        self.abs_min = None
        self.selected_min = None
        self.selected_max = None
        self.enabled_values = []

    # pylint: disable=unused-argument
    def count_self(self, query_index_pk, facets, products=None):
        absolutes = products.product_prices().aggregate(Min(self.attribute), Max(self.attribute))
        self.abs_min = absolutes.get('low_price__min')
        self.abs_max = absolutes.get('low_price__max')
        for value in self.enabled_values:
            self.selected = True
            yield value.asdict()


    def parse_request(self, params: QueryDict):
        try:
            selected_min = params.pop(f'{self.name}_min')
            selected_max = params.pop(f'{self.name}_max')
            if selected_max:
                self.selected_max = decimal.Decimal(selected_max[-1])
            if selected_min:
                self.selected_min = decimal.Decimal(selected_min[-1])
            return params
        except KeyError:
            return params


    def filter_self(self):
        args = {}
        if self.selected_max:
            self.enabled_values.append(
                BaseReturnValue(f'{self.name}_max={self.selected_max}', f'Max {self.name}', None, True)
                )
            args.update({f'{self.attribute}__lte': self.selected_max})
        if self.selected_min:
            self.enabled_values.append(
                BaseReturnValue(f'{self.name}_min={self.selected_min}', f'Min {self.name}', None, True)
                )
            args.update({f'{self.attribute}__gte': self.selected_min})
        if args:
            qset = Product.objects.all().product_prices(self.location_pk)
            self.queryset = qset.filter(**args).values_list('pk', flat=True)
            return self.queryset
        return None

    def serialize_self(self):
        return_dict = {
            'name': self.name,
            'selected': self.selected,
            'widget': 'slider',
            'editabled': False,
            'exclusive': True,
            'abs_min': self.abs_min,
            'abs_max': self.abs_max,
            'selected_min': self.selected_min,
            'selected_max': self.selected_max
            }
        return return_dict
