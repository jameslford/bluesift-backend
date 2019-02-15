from django.shortcuts import render
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from CustomerProfiles.models import (
    CustomerProfile,
    CustomerProject,
    CustomerProduct
    )
from CustomerProfiles.serializers import (
    CustomerLibrarySerializer,
    CustomerProductSerializer,
    CustomerProfileSerializer,
    CustomerProjectSerializer
)
from Products.models import Product
from Addresses.models import Address, Zipcode

@api_view(['GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def customer_library(request):
    user = request.user
    profile = CustomerProfile.objects.get_or_create(user=user)[0]
    # projects = profile.projects.all()
    # if not projects:
    #         projects = CustomerProject.objects.create(owner=profile)

    if request.method == 'GET':
        library = CustomerLibrarySerializer(profile).data
        return Response(library, status=status.HTTP_200_OK)


    if request.method == 'DELETE':
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'DELETE', 'PUT', 'POST'])
@permission_classes((IsAuthenticated,))
def customer_project(request):
    pass





def customer_library_append(request):
    user = request.user
    projects = get_customer_projects(user)
    prod_id = request.POST.get('prod_id')
    project_id = request.POST.get('proj_id', 0)
    product = Product.objects.get(id=prod_id)
    project_count = projects.count()
    if project_id != 0:
        project = projects.get(id=project_id)
        CustomerProduct.objects.create(project=project, product=product)
        return Response(status=status.HTTP_201_CREATED)
    elif project_count == 1:
        project = projects.first()
        CustomerProduct.objects.create(project=project, product=product)
        return Response(status=status.HTTP_201_CREATED)
    return Response(status=status.HTTP_412_PRECONDITION_FAILED)


def customer_short_lib(request):
    user = request.user
    proj_id = request.GET.get('proj_id')
    projects = CustomerProject.objects.filter(owner=user.customer_profile)
    project = projects.first()
    if not project:
        project = CustomerProject.objects.create(owner=user.customer_profile, nickname='First Project')
    projects_list = []
    product_ids = []
    if proj_id:
        project = projects.filter(id=proj_id).first()
    selected_project = {'id': project.id, 'nickname': project.nickname}
    for proj in projects:
        content = {}
        content['nickname'] = proj.nickname
        content['id'] = proj.id
        projects_list.append(content)
    products = project.products.all()
    for prod in products:
        product_ids.append(prod.product.id)
    full_content = {
        'list': projects_list,
        'count': projects.count(),
        'selected_location': selected_project,
        'product_ids': product_ids
    }
    response = {'shortLib': full_content}
    return Response(response, status=status.HTTP_200_OK)
