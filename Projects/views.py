from django.core.exceptions import ValidationError
from django.db.models import Min, Max, F, Sum, DateTimeField, DecimalField, ExpressionWrapper, DurationField
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import OwnerOrAdmin
from Profiles.models import LibraryProduct
from Suppliers.models import SupplierProduct
from .models import Project, ProjectProduct, ProjectTask
from .serializers import serialize_project_detail, reserialize_task, resource_serializer, serialize_task


@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_projects(request):
    projects = request.user.get_collections()
    return_dict = projects.annotate(
        min_date=Min('tasks__start_date'),
        max_date=Max(F('tasks__start_date') + (F('tasks__duration') * (1 - (F('tasks__progress')/100) ) ), output_field=DateTimeField('day')),
        material_cost=Sum(
            F('products__supplier_product__in_store_ppu') * F('products__quantity_needed'),
            output_field=DecimalField(decimal_places=2)),
        additional_costs_sum=Sum('additional_costs__amount'),
        # duration=ExpressionWrapper(
        #     (Max(F('tasks__start_date') + F('tasks__duration'), output_field=DateTimeField('day'))) -
        #     (Min('tasks__start_date')), output_field=DurationField()
        #     ),
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
            # 'duration',
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
        project = request.user.get_collections().filter(pk=project_pk).annotate(
        min_date=Min('tasks__start_date'),
        address_string=F('address__address_string'),
        max_date=Max(F('tasks__start_date') + F('tasks__duration'), output_field=DateTimeField('day')),
        material_cost=Sum(
            F('products__supplier_product__in_store_ppu') * F('products__quantity_needed'),
            output_field=DecimalField(decimal_places=2)),
        additional_costs_sum=Sum('additional_costs__amount'),
        ).values(
            'pk',
            'nickname',
            'address_string',
            # 'lat',
            # 'lng',
            'deadline',
            'min_date',
            'max_date',
            # 'duration',
            'additional_costs_sum',
            'material_cost'
            )[0]

        tasks = [serialize_task(task) for task in ProjectTask.objects.filter(project__pk=project['pk'], level='0')]
        project.update({'tasks': tasks})
        return Response(project)





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
def get_tasks(request: Request, project_pk, task_pk=None):
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
def resources(request, project_pk, product_pk=None):

    project = Project.objects.prefetch_related('tasks', 'products').get(owner__user=request.user, pk=project_pk)
    if request.method == 'GET':
        response = {
            'tasks': project.tasks.values('pk', 'name'),
            'project_products': [resource_serializer(prod) for prod in project.products.all()]
        }
        return Response(response, status=status.HTTP_200_OK)

    if request.method == 'POST':
        library_product = request.POST.get('library_product')
        library_product = LibraryProduct.objects.get(pk=library_product)
        ProjectProduct.objects.get_or_create(
            project=project,
            product=library_product
        )
        return Response(status=status.HTTP_200_OK)

    if request.method == 'PUT':
        data = request.data
        for group in data:
            pk = group.get('pk')
            prod: ProjectProduct = ProjectProduct.objects.get(project=project, pk=pk)
            quant = group.get('quantity', prod.quantity_needed)
            procured = group.get('procured', prod.procured)
            sup = group.get('supplier')
            if sup:
                supplier_product = SupplierProduct.objects.get(pk=sup)
                prod.supplier_product = supplier_product
            task = group.get('task')
            if task:
                ptask = ProjectTask.objects.get(project=project, pk=task)
                prod.linked_tasks = ptask
            prod.quantity_needed = quant
            prod.procured = procured
            prod.save()
        return Response(status=status.HTTP_200_OK)

    if request.method == 'DELETE':
        prod = ProjectProduct.objects.get(project=project, pk=product_pk)
        prod.delete()
        return Response(status=status.HTTP_200_OK)





    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
