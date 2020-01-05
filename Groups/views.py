"""
    views for groups (companies)

"""

from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from config.custom_permissions import OwnerDeleteAdminEdit
from Profiles.models import BaseProfile
from .models import RetailerCompany, ProCompany, Company, ServiceType


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


@api_view(['GET',])
@permission_classes((IsAuthenticated,))
def company_detail(request: Request):
    user = request.user

    if user.is_pro:
        pass

    if user.is_supplier:
        pass

    return Response(status=status.HTTP_200_OK)


@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated, OwnerDeleteAdminEdit))
def company_edit_delete(request: Request):
    if request.method == 'DELETE':
        Company.objects.delete_company(request.user)
        return Response(status=status.HTTP_200_OK)
