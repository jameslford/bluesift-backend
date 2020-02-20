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
from .models import SupplierCompany


# @api_view(['POST'])
# @permission_classes((IsAuthenticated,))
# @transaction.atomic()
# def get_or_create_business(request):
#     pass

@api_view(['GET'])
def public_company_view(request: Request, pk):
    pass



@api_view(['PUT', 'DELETE', 'GET', 'POST'])
@permission_classes((IsAuthenticated, OwnerDeleteAdminEdit))
@transaction.atomic()
def company_crud(request: Request):

    if request.method == 'DELETE':
        SupplierCompany.objects.delete_company(request.user)
        return Response(status=status.HTTP_200_OK)

    if request.method == 'POST':
        user = request.user
        if user.get_profile():
            return Response(f'{user.email} already associated with business', status=status.HTTP_412_PRECONDITION_FAILED)
        data = request.data
        company_name = data.get('company_name')
        title = data.get('role')
        if not company_name:
            return Response('No company name', status=status.HTTP_400_BAD_REQUEST)
        company = SupplierCompany.objects.create_company(user=user, name=company_name)
        profile = BaseProfile.objects.create_profile(user, company=company, title=title, owner=True)
        return Response({'name': company.name}, status=status.HTTP_201_CREATED)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
