"""
Analytics.views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from config.custom_permissions import SupplierorAdmin
from UserProductCollections.models import RetailerLocation
from .models import PlansRecord, ProductViewRecord


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def plan_views(request):
    return Response(PlansRecord.get_values())


@api_view(['GET'])
def department_view(request):
    pass


@api_view(['GET'])
@permission_classes((SupplierorAdmin,))
def all_retailer_location_views(request, group_pk=None):
    locations = None
    user = request.user
    if user.admin:
        if group_pk:
            locations = RetailerLocation.objects.get(retailer_pk=group_pk)
        else:
            locations = RetailerLocation.objects.all()
    if user.is_supplier:
        locations = user.get_collections()
    res = ProductViewRecord.views_time_series(locations)
    return Response(res)




@api_view(['GET'])
def all_retailers_viewed(request):
    locations = RetailerLocation.objects.all()
    location_pks = locations.values_list('pk', flat=True)
    records = ProductViewRecord.objects.select_related(
        'query_index',
        'query_index__retailer_location'
    ).filter(query_index__retailer_location__pk__in=location_pks)
