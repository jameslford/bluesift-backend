"""
Analytics.views
"""
from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models.functions import TruncWeek, TruncDay, TruncMonth, TruncHour
from Accounts.models import User
from .models import ViewRecord
# from rest_framework import status
from config.custom_permissions import SupplierAdminPro
# from UserProductCollections.models import RetailerLocation
# from Groups.models import RetailerCompany


@api_view(['GET'])
# @permission_classes((SupplierAdminPro,))
def view_records(request, interval='day'):
    user: User = request.user
    if user.is_authenticated:
        if user.is_supplier:
            pks = user.get_collections().values_list('pk', flat=True)
            print('pk list is', pks)
            records = ViewRecord.objects.filter(supplier_pk__in=list(pks))
            print('view record count = ', records.count())
        elif user.is_pro:
            pk = user.get_group().pk
            records = ViewRecord.objects.filter(pro_company_pk=pk)
        elif user.admin:
            records = ViewRecord.objects.all()
    else:
        records = ViewRecord.objects.all()
    # recs = records.order_by('recorded').annotate(value=Count('pk')).values('recorded', 'value')
    recs = records.annotate(
            x=TruncDay('recorded')).values(
                'x').annotate(
                    y=Count('pk')).values('x', 'y').order_by('x')
    res = {
        'label': 'all views',
        'data': recs
    }
    return Response(res)

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
