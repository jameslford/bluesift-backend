from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from ProductFilter.models import (
    BaseFacet
    # BoolFacet,
    # MultiFacet,
    # StaticDecimalFacet,
    # StaticRangeFacet,
    # RadiusFacet,
    # DynamicDecimalFacet,
    # DynamicRangeFacet,
    # NonNullFacet
)
from SpecializedProducts.models import (
    FinishSurface,
    Appliance,
    Range,
    # ColdStorage,
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



    BaseFacet.objects.get_or_create(
        content_type=cproduct,
        name='price',
        attribute='low_price',
        field_type='DecimalField'
        )
    BaseFacet.objects.get_or_create(
        content_type=cfs,
        attribute='thickness',
        field_type='DecimalField'
        )
    BaseFacet.objects.get_or_create(
        content_type=cfs,
        attribute='look'
        )
    BaseFacet.objects.get_or_create(
        content_type=cfs,
        attribute='finish'
        )
    BaseFacet.objects.get_or_create(
        content_type=cfs,
        attribute='shade_variation'
        )
    BaseFacet.objects.get_or_create(
        content_type=chardwood,
        attribute='composition'
        )
    BaseFacet.objects.get_or_create(
        content_type=chardwood,
        attribute='species'
        )
    BaseFacet.objects.get_or_create(
        content_type=cresilient,
        attribute='material_type'
        )
    BaseFacet.objects.get_or_create(
        content_type=cresilient,
        attribute='surface_coating'
        )
    BaseFacet.objects.get_or_create(
        content_type=ctas,
        attribute='material_type'
        )
    BaseFacet.objects.get_or_create(
        content_type=capp,
        attribute='width',
        field_type='DecimalRangeField',
        name='width'
        )
    BaseFacet.objects.get_or_create(
        content_type=capp,
        attribute='depth',
        field_type='DecimalRangeField',
        name='depth'
        )
    BaseFacet.objects.get_or_create(
        content_type=ctas,
        attribute='shape',
        name='shape'
        )
    BaseFacet.objects.get_or_create(
        content_type=cresilient,
        attribute='shape',
        name='shape'
        )
    BaseFacet.objects.get_or_create(
        content_type=capp,
        attribute='height',
        field_type='DecimalRangeField',
        name='height'
        )
    BaseFacet.objects.get_or_create(
        content_type=cfs,
        attribute='label_color',
        name='color',
        widget='color',
        editable=False
        )
    BaseFacet.objects.get_or_create(
        content_type=cproduct,
        attribute='locations',
        widget='location',
        field_type='MultiPointField',
        name='Location'
    )
    BaseFacet.objects.get_or_create(
        content_type=cproduct,
        attribute='manufacturer',
        field_type='ForeignKey',
        widget='checkbox',
        name='manufacturers'
    )
    # TODO create url field for facet
    # BaseFacet.objects.get_or_create(
    #     content_type=cproduct,
    #     name='file_types',
    #     attribute_list=[
    #         'dxf_file',
    #         'rfa_file',
    #         'ipt_file',
    #         'dwg_3d_file',
    #         'dwg_2d_file'
    #         ]
    #     )
    BaseFacet.objects.get_or_create(
        content_type=cfs,
        field_type='BooleanField',
        name='applications',
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
