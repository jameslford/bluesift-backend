# from django.shortcuts import render
# from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Products.scripts import FilterSorter

from CustomerProfiles.models import (
    CustomerProfile,
    CustomerProject,
    CustomerProduct,
    CustomerProjectApplication
    )
from CustomerProfiles.serializers import (
    CustomerLibrarySerializer,
    CustomerProjectSerializer,
    CustomerProjectDetailSerializer,
    CustomerProjectApplicationSerializer
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
            'products__product',
            # 'products__product__pk',
            # 'products__product__finish',
            'products__product__label_color',
            'products__product__look',
            'products__product__manufacturer',
            'products__product__swatch_image',
            'products__product__material',
            'applications__products',
            ).filter(id=pk).first()
        # product_ids = project.values_list('products__product__pk', flat=True)
        if not project.owner == profile:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        products = [q.product.pk for q in project.products.all()]
        products = Product.objects.filter(id__in=products)
        sorter = FilterSorter([], [], [])
        # products = sorter.filter_location(products)
        # products = sorter.filter_price(products)
        # products = sorter.filter_thickness(products)

        products = sorter.filter_bools(products)
        products = sorter.filter_attribute(products)

        filter_response = sorter.return_filter(products)

        serialized_project = CustomerProjectDetailSerializer(project)
        return Response({
            'filter': filter_response,
            'project': serialized_project.data
            }, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        pass


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def customer_project_application(request, pk=None):
    user = request.user

    if request.method == 'GET':
        application = CustomerProjectApplication.objects.select_related('project__owner__user').filter(id=pk).first()
        if not application:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if application.project.owner.user != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serialized_app = CustomerProjectApplicationSerializer(application)
        return Response(serialized_app.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        project_id = request.data.get('project', None)
        label = request.data.get('label', None)
        if not project_id or not label:
            return Response('not enough data', status=status.HTTP_400_BAD_REQUEST)
        project = CustomerProject.objects.filter(id=project_id).select_related('project__owner__user').first()
        if not project:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if project.owner.user != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        CustomerProjectApplication.objects.create(label=label, project=project)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        app = CustomerProjectApplication.objects.select_related('project__owner__user').filter(id=pk).first()
        if not app:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        if app.project.owner.user != user:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        app.delete()
        return Response(status=status.HTTP_200_OK)

    if request.method == 'PUT':
        data = request.data
        if not data:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serialized_app = CustomerProjectApplicationSerializer(data=data)
        if not serialized_app.is_valid():
            return Response(serialized_app.errors, status=status.HTTP_400_BAD_REQUEST)
        app_id = data.get('id', None)
        application = CustomerProjectApplication.objects.select_related(
            'project__owner__user').filter(id=app_id).first()
        if not application or application.project.owner.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serialized_app.update(application, data)
        return Response(status=status.HTTP_200_OK)


# @api_view(['DELETE', 'PUT', 'POST'])
# @permission_classes((IsAuthenticated,))
# def customer_project_application_product(request, pk=None):
#     user = request.user

#     if request.method == 'POST':
#         app_id = request.data.get('application_id', None)
#         cus_prod_id = request.data.get('customer_product_id', None)
#         if not app_id or not cus_prod_id:
#             return Response(status=status.HTTP_406_NOT_ACCEPTABLE)
#         application = CustomerProjectApplication.objects.select_related(
#             'project',
#             'project__owner__user').filter(id=app_id).first()
#         cus_product = CustomerProduct.objects.select_related(
#             'project',
#             'project__owner__user').filter(id=cus_prod_id).first()
#         if not application or not cus_product:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         if (application.project.owner.user != user or
#                 cus_product.project.owner.user != user or
#                 application.project != cus_product.project):
#                 return Response(status=status.HTTP_401_UNAUTHORIZED)
#         application.products.add(cus_product)
#         return Response(status=status.HTTP_202_ACCEPTED)

#     if request.method == 'DELETE':
#         pass


@api_view(['DELETE', 'PUT', 'POST', 'GET'])
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

    #expierimental
    if request.method == 'GET':
        products = Product.objects.filter('priced__')


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
