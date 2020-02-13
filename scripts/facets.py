from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from ProductFilter.models import (
    BoolFacet,
    MultiFacet,
    StaticDecimalFacet,
    StaticRangeFacet,
    RadiusFacet,
    DynamicDecimalFacet,
    DynamicRangeFacet
)
from SpecializedProducts.models import (
    FinishSurface,
    Appliance,
    Range,
    ColdStorage,
    Hardwood,
    Resilient,
    TileAndStone,
    LaminateFlooring,
    CabinetLaminate
    )
from Products.models import Product


@transaction.atomic
def create_facets():
    cproduct = ContentType.objects.get_for_model(Product)
    cfs = ContentType.objects.get_for_model(FinishSurface)
    capp = ContentType.objects.get_for_model(Appliance)
    chardwood = ContentType.objects.get_for_model(Hardwood)
    cresilient = ContentType.objects.get_for_model(Resilient)
    ctas = ContentType.objects.get_for_model(TileAndStone)



    DynamicDecimalFacet.objects.get_or_create(
        content_type=cproduct,
        attribute='low_price'
        )
    StaticDecimalFacet.objects.get_or_create(
        contente_type=cfs,
        attribute='thickness'
        )
    MultiFacet.objects.get_or_create(
        contente_type=cfs,
        attribute='look'
        )
    MultiFacet.objects.get_or_create(
        contente_type=cfs,
        attribute='finish'
        )
    MultiFacet.objects.get_or_create(
        contente_type=cfs,
        attribute='shade_variation'
        )
    MultiFacet.objects.get_or_create(
        contente_type=chardwood,
        attribute='composition'
        )
    MultiFacet.objects.get_or_create(
        contente_type=chardwood,
        attribute='species'
        )
    MultiFacet.objects.get_or_create(
        contente_type=cresilient,
        attribute='material_type'
        )
    MultiFacet.objects.get_or_create(
        contente_type=cresilient,
        attribute='surface_coating'
        )
    MultiFacet.objects.get_or_create(
        contente_type=ctas,
        attribute='material_type'
        )
    BoolFacet.objects.get_or_create(
        content_type=cfs,
        attribute_list=[
            'walls',
            'countertops',
            'floors',
            'cabinet_fronts',
            'shower_floors',
            'shower_walls',
            'exterior_walls',
            'exterior_floors',
            'covered_walls',
            'covered_floors',
            'pool_linings',
            'bullnose',
            'covebase',
            'corner_covebase'
            ]
            )
