"""
Higher end admin views for frontend.
Stats from all over return per tab according to frontend organization
Will organise functions up top and pull them per info needed
"""

from dataclasses import dataclass
from dataclasses import field as dfield
from typing import List
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status

from django.contrib.auth import get_user_model
from Accounts.serializers import UserSerializer
from Profiles.models import ConsumerProfile, RetailerEmployeeProfile, ProEmployeeProfile
from Groups.models import RetailerCompany, ProCompany



def get_plans_overview():
    pass


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def dashboard(request):
    pass


    # consumers = ConsumerProfile.objects.filter(plan__isnull=False).count()
    # retailer_companies = RetailerCompany.objects.filter(plan__isnull=False).count()
    # pro_companies = ProCompany.objects.filter(plan__isnull=False).count()
    # labeled_result = LabeledResult([consumers, retailer_companies, pro_companies], label='plans')
    # graph = GraphResponse([labeled_result], ['consumers', 'retailers', 'pros'])
    # return Response(graph.to_dict())





#     user_model = get_user_model()
#     users = user_model.objects.all()
#     serialized_user = UserSerializer(users, many=True)
#     return Response({'users': serialized_user.data})

# @api_view(['POST'])
# @permission_classes((IsAdminUser,))
# def admin_check(request):
#     return Response({'authorized': True})

# @api_view(['POST', 'DELETE'])
# @permission_classes((IsAdminUser,))
# def user_details(request, pk=None):
#     user_model = get_user_model()

#     if request.method == 'DELETE':
#         user = user_model.objects.get(id=pk)
#         deleted_user = user.delete()
#         return Response({'deleted': deleted_user}, status=status.HTTP_202_ACCEPTED) 

