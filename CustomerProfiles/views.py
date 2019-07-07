# from django.shortcuts import render
# from django.conf import settings
# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework import status
# # from Products.scripts import FilterSorter

# from CustomerProfiles.models import (
#     CustomerProfile,
#     CustomerProject,
#     CustomerProduct,
#     CustomerProjectApplication
#     )
# from CustomerProfiles.serializers import (
#     CustomerLibrarySerializer,
#     CustomerProjectSerializer,
#     CustomerProjectDetailSerializer,
#     CustomerProjectApplicationSerializer
# )
# from Products.models import Product, ProductSubClass


# @api_view(['GET', 'DELETE'])
# @permission_classes((IsAuthenticated,))
# def customer_library(request):
#     user = request.user
#     profile = CustomerProfile.objects.get_or_create(user=user)[0]

#     if request.method == 'GET':
#         library = CustomerLibrarySerializer(profile).data
#         return Response(library, status=status.HTTP_200_OK)

#     if request.method == 'DELETE':
#         profile.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)


# @api_view(['GET', 'DELETE', 'PUT', 'POST'])
# @permission_classes((IsAuthenticated,))
# def customer_project(request, pk=None):
#     user = request.user
#     profile = CustomerProfile.objects.filter(user=user).first()
#     if not profile:
#         return Response('Invalid user', status=status.HTTP_400_BAD_REQUEST)

#     if request.method == 'POST':
#         serialized_project = CustomerProjectSerializer(data=request.data)
#         # if not serialized_project.is_valid():
#         #     return Response(serialized_project.errors, status=status.HTTP_400_BAD_REQUEST)
#         serialized_project.create(profile, request.data)
#         return Response(status=status.HTTP_201_CREATED)

#     if request.method == 'DELETE':
#         projects = CustomerProject.objects.filter(owner=profile)
#         project = projects.filter(pk=pk).first()
#         if not project:
#             return Response('Invalid projects', status=status.HTTP_400_BAD_REQUEST)
#         project.delete()
#         return Response(status=status.HTTP_200_OK)

#     if request.method == 'GET':
#         project = CustomerProject.objects.prefetch_related(
#             'products',
#             'products__product',
#             'products__product__manufacturer',
#             'applications__products',
#             ).filter(pk=pk).first()
#         if not project.owner == profile:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         # products = project.products.values_list('product__pk', flat=True).distinct()
#         cats = [cls.__name__ for cls in ProductSubClass.__subclasses__()]

#         serialized_project = CustomerProjectDetailSerializer(project)
#         return Response({
#             'cats': cats,
#             'project': serialized_project.data
#             }, status=status.HTTP_200_OK)

#     if request.method == 'PUT':
#         pass


# @api_view(['GET', 'POST', 'PUT', 'DELETE'])
# @permission_classes((IsAuthenticated,))
# def customer_project_application(request, pk=None):
#     user = request.user

#     if request.method == 'GET':
#         application = CustomerProjectApplication.objects.select_related('project__owner__user').filter(pk=pk).first()
#         if not application:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         if application.project.owner.user != user:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         serialized_app = CustomerProjectApplicationSerializer(application)
#         return Response(serialized_app.data, status=status.HTTP_200_OK)

#     if request.method == 'POST':
#         project_id = request.data.get('project', None)
#         label = request.data.get('label', None)
#         if not project_id or not label:
#             return Response('not enough data', status=status.HTTP_400_BAD_REQUEST)
#         project = CustomerProject.objects.filter(pk=project_id).select_related('owner__user').first()
#         if not project:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         if project.owner.user != user:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         CustomerProjectApplication.objects.create(label=label, project=project)
#         return Response(status=status.HTTP_201_CREATED)

#     if request.method == 'DELETE':
#         app = CustomerProjectApplication.objects.select_related('project__owner__user').filter(pk=pk).first()
#         if not app:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         if app.project.owner.user != user:
#             return Response(status=status.HTTP_401_UNAUTHORIZED)
#         app.delete()
#         return Response(status=status.HTTP_200_OK)

#     if request.method == 'PUT':
#         data = request.data
#         if not data:
#             return Response(status=status.HTTP_400_BAD_REQUEST)
#         serialized_app = CustomerProjectApplicationSerializer(data=data)
#         if not serialized_app.is_valid():
#             return Response(serialized_app.errors, status=status.HTTP_400_BAD_REQUEST)
#         app_id = data.get('id', None)
#         application = CustomerProjectApplication.objects.select_related(
#             'project__owner__user').filter(pk=app_id).first()
#         if not application or application.project.owner.user != user:
#             return Response(status=status.HTTP_403_FORBIDDEN)
#         serialized_app.update(application, data)
#         return Response(status=status.HTTP_200_OK)


# @api_view(['DELETE', 'PUT', 'POST', 'GET'])
# @permission_classes((IsAuthenticated,))
# def customer_product(request, proj_pk, prod_pk=None):
#     user = request.user
#     profile = CustomerProfile.objects.filter(user=user).first()
#     if not profile:
#         profile = CustomerProfile.objects.create(user=user)
#     projects = profile.projects
#     if not projects:
#         CustomerProject.objects.create(owner=profile)
#     project = projects.first()
#     if proj_pk:
#         project = projects.filter(pk=proj_pk).first()

#     if request.method == 'POST':
#         prod_pk = request.POST.get('prod_pk', None)
#         product = Product.objects.filter(pk=prod_pk).first()
#         if product:
#             CustomerProduct.objects.create(product=product, project=project)
#             return Response(status=status.HTTP_201_CREATED)

#     if request.method == 'DELETE':
#         if not prod_pk:
#             return Response('No product specified for deletion', status=status.HTTP_400_BAD_REQUEST)
#         cus_product: CustomerProduct = project.products.filter(product__pk=prod_pk).first()
#         if cus_product:
#             cus_product.delete()
#             return Response(status=status.HTTP_202_ACCEPTED)

#     return Response(status=status.HTTP_400_BAD_REQUEST)


# def customer_short_lib(request):
#     user = request.user
#     proj_id = request.GET.get('proj_id', None)
#     prod_id = request.GET.get('prod_id', None)
#     profile = CustomerProfile.objects.get_or_create(user=user)[0]
#     projects = CustomerProject.objects.filter(owner=profile)
#     project = projects.first()
#     if not project:
#         project = CustomerProject.objects.create(owner=user.customer_profile, nickname='First Project')
#     projects_list = []
#     # product_ids = []
#     if proj_id:
#         project = projects.filter(pk=proj_id).first()
#     selected_project = {'pk': project.pk, 'nickname': project.nickname}
#     for proj in projects:
#         content = {}
#         content['nickname'] = proj.nickname
#         content['pk'] = proj.pk
#         content['remove'] = False
#         for k in proj.products.select_related('product').all():
#             if k.product.pk == prod_id:
#                 content['remove'] = True
#                 content['cprod'] = k.pk
#         projects_list.append(content)
#     products = project.products.all()
#     selected_product_ids = [q.product.pk for q in products]
#     full_content = {
#         'list': projects_list,
#         'count': projects.count(),
#         'selected_location': selected_project,
#         'product_ids': selected_product_ids
#     }
#     return Response(full_content, status=status.HTTP_200_OK)
