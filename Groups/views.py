"""
    views for groups (companies). includes 5 main views:

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

from django.db.models import Count
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from config.custom_permissions import OwnerDeleteAdminEdit
from config.views import check_department_string
from Retailers.models import RetailerLocation
from Profiles.models import BaseProfile
from .serializers import BusinessSerializer
from .models import RetailerCompany, ProCompany, Company, ServiceType
from .tasks import add_pro_record


@api_view(['POST'])
@permission_classes((IsAuthenticated,))
@transaction.atomic()
def get_or_create_business(request):
    user = request.user
    if user.get_profile():
        return Response(f'{user.email} already associated with business', status=status.HTTP_412_PRECONDITION_FAILED)
    data = request.data
    company_name = data.get('company_name')
    service_type = data.get('service_type', 'contractor')
    title = data.get('role')
    if not company_name:
        return Response('No company name', status=status.HTTP_400_BAD_REQUEST)
    service_type = ServiceType.objects.filter(label__icontains=service_type).first()
    if user.is_pro and not service_type:
        return Response('Invalid service type', status=status.HTTP_400_BAD_REQUEST)
    company: Company = Company.objects.create_company(user=user, name=company_name, service=service_type)
    profile = BaseProfile.objects.create_profile(user, company=company, title=title, owner=True)
    return Response({'name': company.name}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def retailer_company_detail_public(request: Request, retailer_pk=None):
    if retailer_pk:
        company = RetailerCompany.objects.prefetch_related(
            'employees',
            'employees__user'
        ).get(pk=retailer_pk)
    else:
        if not request.user.is_authenticated or not request.user.is_supplier:
            return Response('No Company specified', status=status.HTTP_400_BAD_REQUEST)
        company = request.user.get_group()
    return Response(BusinessSerializer(company).getData(), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def retailer_company_detail(request: Request):
    pass


@api_view(['GET'])
def pro_company_detail_public(request: Request, pk=None):
    user = request.user
    if not pk:
        if user.is_authenticated and user.is_pro:
            pk = user.get_group().pk
        else:
            return Response('No company verified', status=status.HTTP_400_BAD_REQUEST)
    service: ProCompany = ProCompany.objects.select_related(
        'business_address',
        'business_address__postal_code',
        'business_address__coordinates',
        'plan'
    ).get(pk=pk)
    add_pro_record.delay(request.get_full_path(), pk=pk)
    return Response(
        BusinessSerializer(service).getData(),
        status=status.HTTP_200_OK
        )

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def pro_company_detail(request: Request):
    pass



@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated, OwnerDeleteAdminEdit))
def company_edit_delete(request: Request):
    if request.method == 'DELETE':
        Company.objects.delete_company(request.user)
        return Response(status=status.HTTP_200_OK)
