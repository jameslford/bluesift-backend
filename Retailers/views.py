import datetime
from django.http.request import HttpRequest
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.globals import check_department_string
from config.custom_permissions import RetailerPermission
from config.serializers import BusinessSerializer
from Profiles.models import RetailerEmployeeProfile
from .models import RetailerLocation, RetailerProduct
from .serializers import FullRetailerProductSerializer


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def locations(request):
    # TODO locations view for retailer workbench
    pass



@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated, RetailerPermission))
def crud_location(request: Request, pk: int = None):
    """
    create, update, delete endpoint for RetailerLocation objects
    """
    user = request.user

    if request.method == 'GET':
        location = user.get_collections().get(pk=pk)
        return Response(BusinessSerializer(location, True).getData(), status=status.HTTP_200_OK)

    if request.method == 'POST':
        data = request.data
        RetailerLocation.objects.create_location(user, **data)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'PUT':
        data = request.data
        location = RetailerLocation.objects.update_location(user, **data)
        return Response(BusinessSerializer(location).getData(), status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        profile = user.get_profile()
        if profile.owner:
            location = user.get_collections.all().filter(pk=pk).first()
            location.delete()
            return Response(status=status.HTTP_200_OK)

    return Response('unsupported method', status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET', 'PUT'])
@permission_classes((IsAuthenticated, RetailerPermission))
def retailer_products(request: HttpRequest, product_type=None, location_pk=None):

    if request.method == 'GET':
        model = check_department_string(product_type)
        pks = model.objects.values_list('pk', flat=True)
        location = request.user.get_collections().get(pk=location_pk)
        products = location.products.select_related(
            'product',
            'product__manufacturer'
        ).filter(pk__in=pks)
        # TODO:try to use values instead of a serializer for this. also allow product type filter
        return Response(FullRetailerProductSerializer(products, many=True).data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        data = request.data
        profile: RetailerEmployeeProfile = request.user.get_profile()
        # location_pks = [location.pk for location in request.user.get_collections()]
        location = data.get('location_pk')
        location: RetailerLocation = request.user.get_collections().get(pk=location)
        if not (profile == location.local_admin or
                profile.owner or
                profile.admin):
            return Response('unauthorized', status=status.HTTP_401_UNAUTHORIZED)
        changes = data.get('changes')
        updates = 0
        for change in changes:
            product_pk = change.get('pk')
            product: RetailerProduct = location.products.filter(pk=product_pk).first()
            if not product:
                continue
            in_store_ppu = data.get('in_store_ppu' )
            units_available_in_store = data.get('units_available_in_store')
            lead_time_ts = data.get('lead_time_ts')
            lead_time_ts = datetime.timedelta(days=lead_time_ts)
            product.update(
                in_store_ppu=in_store_ppu,
                units_available_in_store=units_available_in_store,
                lead_time_ts=lead_time_ts
                )
            updates += 1
        return Response(f'{updates} products updated', status=status.HTTP_200_OK)
