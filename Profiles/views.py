from django.shortcuts import render


from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from Profiles.models import CompanyAccount, CompanyShippingLocation, CustomerProfile
from Products.models import Product
# Create your views here.


@api_view(['GET','POST'])
@permission_classes((IsAuthenticated,))
def user_library(request):
    products = Product.objects.all()
    user = request.user
    if user.is_supplier == True:
        return HttpResponse('wrong endpoint: user is supplier')
    else:
        try:
            user.user_library
        except (UserLibrary.DoesNotExist):
            UserLibrary.objects.create(owner=user)
        library = user.user_library
        lib_products = library.products.all()
        serialized_products = ProductSerializer(lib_products, many=True)

        if request.method == 'POST':
            prod_id = request.POST.get('prod_id')
            product = products.get(id=prod_id)
            library.products.add(product)
            library.save()
            return Response({"library" : serialized_products.data})
        elif request.method == 'GET':
            return Response({"library" : serialized_products.data})