""" views for groups (companies). includes 5 main views:

    - retailer_company_header
    - retailer_location_list_all
    - retailer_location_detail_header
    - services_list_all
    - services_detail_header

    Retailer-location views should technically be in the UserProductCollections models since
    they are instances of RetailerLocations instead of RetailerCompany's.
    However, to keep the frontend calls simple, it makes more sense to have these essentially symmetrical
    views in the same module, and therefore same root url
"""

from django.http import HttpRequest
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from UserProductCollections.models import RetailerLocation
from .serializers import (
    ProListSerializer,
    RetailerListSerializer,
    RetailerCompanyHeaderSerializer,
    RetailerLocationHeaderSerializer
)
from .models import RetailerCompany, ProCompany


@api_view(['GET'])
def retailer_company_header(request: HttpRequest, retailer_pk=None):
    if retailer_pk:
        company = RetailerCompany.objects.get(pk=retailer_pk)
    else:
        if not request.user.is_authenticated() and request.user.is_supplier:
            return Response('No Company specified', status=status.HTTP_400_BAD_REQUEST)
        company = request.user.get_group()
    return Response(RetailerCompanyHeaderSerializer(company), status=status.HTTP_200_OK)


@api_view(['GET'])
def retailer_location_list_all(request: HttpRequest, prod_type='all'):
    retailers = RetailerLocation.objects.select_related(
        'address',
        'address__postal_code',
        'address__coordinates',
        'company'
        ).prefetch_related(
            'products',
            'products__product'
            ).all().annotate(prod_count=Count('products'))
    if prod_type.lower() != 'all':
        from Products.models import ProductSubClass
        prod_class = ProductSubClass.return_sub(prod_type)
        if prod_class is None:
            return Response('invalid model type', status=status.HTTP_400_BAD_REQUEST)
        retailer_product_pks = prod_class.objects.retailer_products().values('retailer__pk')
        retailers = retailers.filter(pk__in=retailer_product_pks)
    return Response(
        RetailerListSerializer(retailers, many=True).data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def retailer_location_detail_header(request: HttpRequest, pk):
    retailer = RetailerLocation.objects.select_related(
        'address',
        'address__postal_code',
        'address__coordinates',
        'company',
        ).prefetch_related('products').get(pk=pk)
    return Response(
        RetailerLocationHeaderSerializer(retailer).data,
        status=status.HTTP_200_OK
        )


@api_view(['GET'])
def services_list_all(request: HttpRequest, cat='all'):
    services = ProCompany.objects.select_related(
        'business_address',
        'business_address__postal_code',
        'business_address__coordinates'
    ).all()
    if cat.lower() != 'all':
        services = services.filter(service__label__iexact=cat)
    return Response(
        ProListSerializer(services, many=True).data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def service_detail_header(request: HttpRequest, pk):
    service = ProCompany.objects.select_related(
        'business_address',
        'business_address__postal_code',
        'business_address__coordinates'
    ).get(pk=pk)
    return Response(
        ProListSerializer(service).data,
        status=status.HTTP_200_OK
        )
