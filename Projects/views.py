from django.core.exceptions import ValidationError
from django.db.models import Min, Max, F, Sum, DateTimeField, DecimalField, ExpressionWrapper, DurationField
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import OwnerOrAdmin
from Profiles.models import LibraryProduct
from .models import Project, ProjectProduct
from .serializers import serialize_project_detail, reserialize_task, resource_serializer


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_projects(request):
    projects = request.user.get_collections()
    return_dict = projects.annotate(
        min_date=Min('tasks__start_date'), 
        max_date=Max(F('tasks__start_date') + F('tasks__duration'), output_field=DateTimeField('day')),
        material_cost=Sum(
            F('products__retailer_product__in_store_ppu') * F('products__quantity_needed'),
            output_field=DecimalField(decimal_places=2)),
        additional_costs_sum=Sum('additional_costs__amount'),
        duration=ExpressionWrapper(
            (Max(F('tasks__start_date') + F('tasks__duration'), output_field=DateTimeField('day'))) -
            (Min('tasks__start_date')), output_field=DurationField()
            ),
        address_string=F('address__address_string'),
        lat=F('address__coordinates__lat'),
        lng=F('address__coordinates__lng'),
        ).values(
            'pk',
            'nickname',
            'address_string',
            'lat',
            'lng',
            'deadline',
            'min_date',
            'max_date',
            'duration',
            'additional_costs_sum',
            'material_cost'
            )
    return Response(return_dict, status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated, OwnerOrAdmin))
def dashboard(request: Request, project_pk=None):
    """
    sole endpoint to add a project - model manager will differentiate between user and pro_user
    """
    if request.method == 'GET':
        project = request.user.get_collections().select_related(
            'address',
            'address__postal_code'
            ).filter(pk=project_pk).first()
        return Response(serialize_project_detail(project))

    if request.method == 'POST':
        try:
            project = Project.objects.create_project(request.user, **request.data)
            return Response(status=status.HTTP_201_CREATED)
        except ValidationError as error:
            return Response(error.messages[1], status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'DELETE':
        project = request.user.get_collections().filter(pk=project_pk).first()
        if not project:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        project.delete()
        return Response(status=status.HTTP_200_OK)

    if request.method == 'PUT':
        user = request.user
        data = request.data
        project = Project.objects.update_project(user, **data)
        return Response(serialize_project_detail(project), status=status.HTTP_200_OK)

    return Response('Unsupported method', status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['POST', 'DELETE'])
@permission_classes((IsAuthenticated, OwnerOrAdmin))
def tasks(request: Request, project_pk, task_pk=None):
    project = Project.objects.get_user_projects(request.user, project_pk)
    if request.method == 'POST':
        data = request.data
        children = data.get('children', None)
        if children:
            for child in children:
                reserialize_task(project, child)
            return Response('children created', status=status.HTTP_200_OK)
        return Response(status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        task = project.tasks.get(pk=task_pk)
        task.delete()
        return Response(status=status.HTTP_200_OK)

            # 'product__product__product',
            # 'product__product__product__priced'

@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated, OwnerOrAdmin))
def resources(request, pk):

    if request.method == 'GET':
        products = ProjectProduct.objects.select_related(
            'product__product').filter(project__owner__user__pk=request.user.pk, project__pk=pk)
        products = [resource_serializer(prod) for prod in products]
        return Response(products, status=status.HTTP_200_OK)

    if request.method == 'POST':
        library_product = request.POST.get('library_product')
        library_product = LibraryProduct.objects.get(pk=library_product)
        project: Project = Project.objects.get(pk=pk)
        ProjectProduct.objects.get_or_create(
            project=project,
            product=library_product
        )
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
