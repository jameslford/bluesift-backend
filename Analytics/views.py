from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from UserProductCollections.models import RetailerLocation
from .models import PlansRecord, ProductViewRecord
# from .serializers import ProductViewRecordSerializer


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def plan_views(request):
    return Response(PlansRecord.get_values())


@api_view(['GET'])
def department_view(request):
    pass


@api_view(['GET'])
def retailer_view_analytics(request):
    locations = request.user.get_collections().values_list('pk', flat=True)
    locations = RetailerLocation.objects.prefetch_related(
        'qis',
        'qis__record'
    ).filter(pk__in=locations)
    response = []
    for location in locations:
        loc_dict = {
            'nickname': location.nickname,
            'pk': location.pk,
            'queries': []
            }
        for index in location.qis.all():
            qi_dict = {
                'query_dict': index.query_dict,
                'accessed': [record.created for record in index.record.all()]
            }
            loc_dict['queries'].append(qi_dict)
        response.append(loc_dict)
    return Response(response)


    # records = ProductViewRecord.objects.select_related(
    #     'query_index',
    #     'query_index__retailer_location'
    # ).filter(query_index__retailer_location__pk__in=location_pks)
    # res = []
    # for location in locations:
    #     loc_recs = records.filter(query_index__retailer_location__pk=location.pk)
    #     response = {
    #         'location': location.nicname,
    #         'queries': []
    #         }
    #     qis = location.qis.all()
    #     for qi in qis:

    #         for record in qi.record.all():
    #             blah.append(record)
