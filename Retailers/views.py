
from django.core.exceptions import PermissionDenied
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import RetailerPermission
from Groups.serializers import BusinessSerializer
from .models import RetailerLocation, RetailerProduct
from .tasks import add_retailer_record
from .serializers import FullRetailerProductSerializer


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def locations(request):
    pass

@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated, RetailerPermission))
def crud_location(request: Request, location_pk: int = None):
    """
    create, update, delete endpoint for RetailerLocation objects
    """
    user = request.user

    if request.method == 'GET':
        add_retailer_record.delay(request.get_full_path(), location_pk)
        location = RetailerLocation.objects.get(pk=location_pk)
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
            location = user.get_collections.all().filter(pk=location_pk).first()
            location.delete()
            return Response(status=status.HTTP_200_OK)

    return Response('unsupported method', status=status.HTTP_405_METHOD_NOT_ALLOWED)

@api_view(['PUT'])
@permission_classes((IsAuthenticated, RetailerPermission))
def edit_retailer_product(request: Request):
    data = request.data
    updates = 0
    try:
        updates = RetailerProduct.objects.update_product(request.user, **data)
    except PermissionDenied:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return Response(f'{updates} products updated', status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAuthenticated, RetailerPermission))
def retailer_products(request, location_pk):
    location = request.user.get_collections().get(pk=location_pk)
    products = location.products.select_related(
        'product',
        'product__manufacturer'
    ).all()
    return Response(FullRetailerProductSerializer(products, many=True).data, status=status.HTTP_200_OK)
