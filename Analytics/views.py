"""
Analytics.views
"""
from django.db.models import Count
from django.db.models.functions import TruncDay
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from config.custom_permissions import SupplierAdminPro
from rest_framework.response import Response
from Accounts.models import User
# from .models import ViewRecord


# @api_view(['GET'])
# @permission_classes((IsAuthenticated, SupplierAdminPro,))
# def view_records(request, interval='day'):
#     user: User = request.user
#     if user.is_authenticated:
#         if user.is_supplier:
#             pks = user.get_collections().values_list('pk', flat=True)
#             print('pk list is', pks)
#             records = ViewRecord.objects.filter(supplier_pk__in=list(pks))
#             print('view record count = ', records.count())
#         elif user.admin:
#             records = ViewRecord.objects.all()
#     else:
#         records = ViewRecord.objects.all()
#     recs = records.annotate(
#             x=TruncDay('recorded')).values(
#                 'x').annotate(
#                     y=Count('pk')).values('x', 'y').order_by('x')
#     res = {
#         'label': 'all views',
#         'data': recs
#     }
#     return Response(res)
