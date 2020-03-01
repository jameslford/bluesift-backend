from typing import List
from django.contrib.contenttypes.models import ContentType
from .base import BaseFacet, QueryIndex
from .bool import BoolFacet
from .char import CharFacet
from .foreign import ForeignFacet
from .location import LocationFacet
from .numeric import NumericFacet
from .availability import AvailabilityFacet
from .price import PriceFacet

def class_map(facet: BaseFacet):
    classmap = {
        'DecimalField': NumericFacet,
        'FloatField': NumericFacet,
        'RangeField': NumericFacet,
        'DecimalRangeField': NumericFacet,
        'FloatRangeField': NumericFacet,
        'CharField': CharFacet,
        'BooleanField': BoolFacet,
        'MultiPointField': LocationFacet,
        'ForeignKey': ForeignFacet
        }
    facet.__class__ = classmap.get(facet.field_type)
    return facet


def load_facets(product_type, supplier_pk):
    special_facet = [AvailabilityFacet(product_type, supplier_pk), PriceFacet(supplier_pk)]
    model_types = product_type._meta.get_parent_list() + [product_type]
    parents = [ContentType.objects.get_for_model(mod) for mod in model_types]
    facets = [class_map(facet) for facet in BaseFacet.objects.filter(content_type__in=parents)]
    return special_facet + facets
