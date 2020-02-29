from django.db.models import Min, Max
from django.db.models.functions import Upper, Lower
from Products.models import Product
from django.http import QueryDict
from .base import BaseFacet, BaseReturnValue


class NumericFacet(BaseFacet):

    class Meta:
        proxy = True


    def __get_absolutes(self):
        print('in get absolutes')
        if self.field_type not in ['DecimalField', 'FloatField', 'RangeField', 'DecimalRangeField', 'FloatRangeField']:
            return None

        if self.abs_min and self.abs_max:
            return [self.abs_max, self.abs_min]


        # if self.attribute == 'low_price':
        #     print('in get absolutes -- low price')
        #     absolutes = Product.objects.product_prices().aggregate(Min(self.attribute), Max(self.attribute))
        #     abs_min = absolutes.get('low_price__min')
        #     abs_max = absolutes.get('low_price__max')
        #     return [abs_max, abs_min]

        else:

            if self.field_type in ['RangeField', 'DecimalRangeField', 'FloatRangeField']:
                kwargs = {'min': Min(Lower(self.attribute)), 'max': Max(Upper(self.attribute))}
            else:
                kwargs = {'min': Min(self.attribute), 'max': Max(self.attribute)}


            if self.others_intersection:
                absolutes = self.others_intersection.aggregate(**kwargs)
                print('others intersection exist', absolutes)
            else:
                absolutes = self.model.objects.aggregate(**kwargs)
                print('no others intersection', absolutes)

        abs_min = absolutes.get('min')
        abs_max = absolutes.get('max')
        if not self.dynamic:
            self.abs_min = abs_min
            self.abs_max = abs_max
            self.save()
        return [abs_max, abs_min]

    def count_self(self, query_index_pk, facets, products=None):
        if not self.dynamic:
            products = self.model.objects.all()
            _facets = [facet.queryset for facet in facets]
            self.get_intersection(query_index_pk, products, _facets)
        for value in self.enabled_values:
            self.selected = True
            yield value.asdict()


    def parse_request(self, params: QueryDict):
        if self.dynamic:
            try:
                self.selected_min = params.pop(f'{self.name}_min')
                self.selected_max = params.pop(f'{self.name}_max')
                return params
            except KeyError:
                return params
        try:
            self.selected_min = params.get(f'{self.name}_min')
            self.selected_max = params.get(f'{self.name}_max')
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
        # if self.attribute == 'low_price':
        #     qset = Product.objects.all().product_prices()
        #     self.queryset = qset.filter(**args).values_list('pk', flat=True)
        #     return self.queryset
        if args:
            self.queryset = self.model.objects.filter(**args).values_list('pk', flat=True)
            return self.queryset
        return None

    def serialize_self(self):
        return_dict = super().serialize_self()
        abs_list = self.__get_absolutes()
        return_dict.update({'abs_min': abs_list[1]})
        return_dict.update({'abs_max': abs_list[0]})
        return_dict.update({'selected_min': self.selected_min})
        return_dict.update({'selected_max': self.selected_max})
        return return_dict
