"""
Analytics.views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from django.db.models.functions import TruncWeek, TruncDay, TruncMonth
from .models import ViewRecord
# from rest_framework import status
# from config.custom_permissions import SupplierorAdmin
# from UserProductCollections.models import RetailerLocation
# from Groups.models import RetailerCompany


@api_view(['GET'])
# @permission_classes((IsAdminUser,))
def view_records(request):
    records = ViewRecord.objects.all()
    recs = records.order_by('recorded').values_list('recorded', 'session_id')
    return Response(recs)

#     pass

# @api_view(['GET'])
# @permission_classes((IsAdminUser,))
# def plan_views(request):
#     return Response(PlansRecord.get_values())


# @api_view(['GET'])
# @permission_classes((SupplierorAdmin,))
# def all_retailer_location_views(request, group_pk=None):
#     locations = None
#     user = request.user
#     if user.admin:
#         if not group_pk:
#             return Response('no group specified')
#         locations = RetailerLocation.objects.filter(company__pk=group_pk)
#     if user.is_supplier:
#         locations = user.get_collections()
#     res = ProductViewRecord.views_time_series(locations)
#     return Response(res)


# @api_view(['GET'])
# @permission_classes((SupplierorAdmin,))
# def group_views(request):
#     groups = RetailerCompany.objects.all()
#     res = ProductViewRecord.views_time_series(groups)
#     return Response(res)


# @api_view(['GET'])
# def test(request, group_pk, interval='day'):
#     locations = RetailerLocation.objects.filter(company__pk=group_pk)
#     res = ProductViewRecord.views_time_series(locations, interval)
#     return Response(res)



# @api_view(['GET'])
# def all_retailers_viewed(request):
#     locations = RetailerLocation.objects.all()
#     location_pks = locations.values_list('pk', flat=True)
#     records = ProductViewRecord.objects.select_related(
#         'query_index',
#         'query_index__retailer_location'
#     ).filter(query_index__retailer_location__pk__in=location_pks)
