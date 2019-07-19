from django.shortcuts import render
from django.http import HttpRequest
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from UserProductCollections.models import RetailerLocation
from .serializers import ProListSerializer, RetailerListSerializer
from .models import RetailerCompany, ProCompany


@api_view(['GET'])
def retailer_list_all(request: HttpRequest):
    retailers = RetailerLocation.objects.select_related(
        'address',
        'address__postal_code',
        'address__coordinates',
        'company'
        ).prefetch_related(
            'products',
            'products__product'
            ).all().annotate(prod_count=Count('products'))
    return Response(
        RetailerListSerializer(retailers, many=True).data,
        status=status.HTTP_200_OK
        )


@api_view(['GET'])
def services_list_all(request: HttpRequest, cat='all'):
    services = ProCompany.objects.select_related(
        'business_address',
        'business_address__postal_code',
        'business_address__coordinates'
    ).all()
    if cat != 'all':
        services = services.filter(service__label__iexact=cat)
    return Response(
        ProListSerializer(services, many=True).data,
        status=status.HTTP_200_OK
    )


@api_view(['GET'])
def retailer_detail_header(request: HttpRequest, pk):
    retailer = RetailerLocation.objects.select_related(
        'address',
        'address__postal_code',
        'address__coordinates',
        'company',
        ).prefetch_related('products').get(pk=pk)
    return Response(
        RetailerListSerializer(retailer).data,
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


