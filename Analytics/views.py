from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .models import PlansRecord


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def plan_views(request):
    return Response(PlansRecord.get_values())


@api_view(['GET'])
def department_view(request):
    pass
