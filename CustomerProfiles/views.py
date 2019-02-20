# from django.shortcuts import render
# from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from CustomerProfiles.models import (
    CustomerProfile,
    CustomerProject,
    CustomerProduct,
    CustomerProjectApplication
    )
from CustomerProfiles.serializers import (
    CustomerLibrarySerializer,
    CustomerProjectSerializer,
    CustomerProjectDetailSerializer
)
from Products.models import Product


@api_view(['GET', 'DELETE'])
@permission_classes((IsAuthenticated,))
def customer_library(request):
    user = request.user
    profile = CustomerProfile.objects.get_or_create(user=user)[0]

    if request.method == 'GET':
        library = CustomerLibrarySerializer(profile).data
        return Response(library, status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET', 'DELETE', 'PUT', 'POST'])
@permission_classes((IsAuthenticated,))
def customer_project(request, pk=None):
    user = request.user
    profile = CustomerProfile.objects.filter(user=user).first()
    if not profile:
        return Response('Invalid user', status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'POST':
        serialized_project = CustomerProjectSerializer(data=request.data)
        if not serialized_project.is_valid():
            return Response(serialized_project.errors, status=status.HTTP_400_BAD_REQUEST)
        serialized_project.create(profile, request.data)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        projects = CustomerProject.objects.filter(owner=profile)
        project = projects.filter(id=pk).first()
        if not project:
            return Response('Invalid projects', status=status.HTTP_400_BAD_REQUEST)
        project.delete()
        return Response(status=status.HTTP_200_OK)

    if request.method == 'GET':
        project = CustomerProject.objects.prefetch_related(
            'products',
            'applications').filter(id=pk).first()
        if not project.owner == profile:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serialized_project = CustomerProjectDetailSerializer(project)
        return Response(serialized_project.data, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        pass

@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated,))
def customer_project_application(request, pk=None):
    user = request.user

    if request.method == 'POST':
        project_id = request.data.get('project', None)
        label = request.data.get('label', None)
        if not project_id or not label:
            return Response('not enough data', status=status.HTTP_400_BAD_REQUEST)
        project = CustomerProject.objects.filter(id=project_id).first()
        if not project:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if project.owner.user != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        CustomerProjectApplication.objects.create(label=label, project=project)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        app = CustomerProjectApplication.objects.filter(id=pk).first()
        if not app:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if app.project.owner.user != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        app.delete()
        return Response(status=status.HTTP_200_OK)

@api_view(['DELETE', 'PUT', 'POST'])
@permission_classes((IsAuthenticated,))
def customer_product(request, pk=None):
    user = request.user
    profile = CustomerProfile.objects.filter(user=user).first()
    if not profile:
        profile = CustomerProfile.objects.create(user=user)

    if request.method == 'POST':
        prod_id = request.POST.get('prod_id')
        project_id = request.POST.get('proj_id', None)
        # projects = CustomerProject.objects.filter(owner=user)
        projects = profile.projects
        if not projects:
            CustomerProject.objects.create(owner=profile)

        product = Product.objects.filter(id=prod_id).first()
        if not product:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if projects.count() == 1:
            project = projects.first()
            CustomerProduct.objects.create(product=product, project=project)
            return Response(status=status.HTTP_201_CREATED)
        if project_id:
            project = projects.filter(id=project_id).first()
            if not project:
                return Response('Invalid project number', status=status.HTTP_400_BAD_REQUEST)
            CustomerProduct.objects.create(product=product, project=project)
            return Response(status=status.HTTP_201_CREATED)
        else:
            return Response('No project specified', status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        if not pk:
            return Response('No product specified for deletion', status=status.HTTP_400_BAD_REQUEST)
        product = CustomerProduct.objects.select_related('project', 'project__owner').filter(pk=pk).first()
        if not product:
            return Response('Invalid product id', status=status.HTTP_400_BAD_REQUEST)
        if product.project.owner != profile:
            return Response('Not your product to delete', status=status.HTTP_400_BAD_REQUEST)
        product.delete()
        return Response(status=status.HTTP_202_ACCEPTED)


def customer_short_lib(request):
    user = request.user
    proj_id = request.GET.get('proj_id')
    profile = CustomerProfile.objects.get_or_create(user=user)[0]
    projects = CustomerProject.objects.filter(owner=profile)
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
