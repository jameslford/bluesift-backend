from django.core.exceptions import ValidationError
from django.db.models import Min, Max, F, Sum, DateTimeField, DecimalField, ExpressionWrapper, DurationField
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import OwnerOrAdmin
from .models import Project
from .serializers import serialize_project_detail, reserialize_task, DAY

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def all_projects(request):
    projects = request.user.get_collections()
    return_dict = projects.annotate(
        min_date=Min('tasks__start_date'), 
        max_date=Max(F('tasks__start_date') + F('tasks__duration'), output_field=DateTimeField('day')),
        material_cost=Sum(
            F('tasks__retailer_product__in_store_ppu') * F('tasks__quantity_needed'),
            output_field=DecimalField(decimal_places=2)),
        additional_costs_sum=Sum('additional_costs__amount'),
        duration=ExpressionWrapper(
            (Max(F('tasks__start_date') + F('tasks__duration'), output_field=DateTimeField('day'))) -
            (Min('tasks__start_date')), output_field=DurationField()
            ),
        bid_sum=Sum('bids__amount')
        ).values(
            'pk',
            'nickname',
            'deadline',
            'min_date',
            'max_date',
            'duration',
            'additional_costs_sum',
            'bid_sum',
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



# @api_view(['POST', 'DELETE'])
# def assignments(request: Request, project_pk, assignment_pk=None):

#     project = request.user.get_collections().get(pk=project_pk)

#     if request.method == 'POST':
#         ProductAssignment.objects.update_assignments(project, *request.data)
#         return Response(status=status.HTTP_201_CREATED)

#     if request.method == 'DELETE':
#         assignment = project.product_assignments.get(pk=assignment_pk)
#         assignment.delete()
#         return Response('deleted')

#     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)



    # if request.method == 'GET':
    #     p_tasks = project.tasks.select_related(
    #         'product',
    #         'user_collaborator',
    #         'pro_collaborator'
    #     ).filter(level=0)
    #     res = [serialize_task(task) for task in p_tasks]
    #     if not res:
    #         res = [{
    #             'name': 'New Major Task',
    #             'children': []
    #         }]
    #     assignments = project.product_assignments.select_related(
    #         'product',
    #         'product__manufacturer'
    #         ).all()
    #     project_node = {
    #         'assignments': [serialize_product_assignment(assi) for assi in assignments],
    #         'project_name': project.nickname,
    #         'project_deadline': project.deadline,
    #         'tasks': res
    #         }
    #     project_node = 'foo'
    #     return Response(project_node, status=status.HTTP_200_OK)

    # if request.method == 'GET':
    #     project = Project.objects.get_user_projects(request.user, project_pk)
    #     project_product_pks = project.products.all().values_list('product__pk', flat=True)
    #     products = Product.subclasses.prefetch_related(
    #         'priced',
    #         'priced__retailer'
    #         ).select_related('manufacturer').filter(pk__in=project_product_pks).select_subclasses()
    #     res = []
    #     for kls in ProductSubClass.__subclasses__():
    #         kls_res = {
    #             'name': kls.__name__,
    #             # 'products': [serialize_product_priced(product) for product in products if isinstance(product, kls)]
    #             }
    #         res.append(kls_res)
    #     assignments = project.product_assignments.select_related(
    #         'product',
    #         'product__manufacturer'
    #         ).all()
    #     response = {
    #         # 'assignments': [serialize_product_assignment(assi) for assi in assignments],
    #         'categories': [cat.__name__ for cat in ProductSubClass.__subclasses__()],
    #         'groups': res
    #         }
    #     return Response(response)

# @api_view(['GET', 'POST', 'DELETE', 'PUT'])
# @permission_classes((IsAuthenticated,))
# def collaborators(request: Request, pk=None):

#     if request.method == 'GET':
#         project = Project.objects.get_user_projects(request.user, pk)
#         pro_collabs = project.pro_collaborators.all().select_related('collaborator', 'contact', 'contact__user')
#         user_collabs = project.collaborators.all().select_related('collaborator')
#         return Response({
#             'pro_collaborators': [col.serialize() for col in pro_collabs],
#             'user_collaborators': [col.serialize() for col in user_collabs]
#         }, status=status.HTTP_200_OK)

#     if request.method == 'POST':
#         pass
        # project = Project.objects.get_user_projects(request.user, pk)
        # service_pk = request.data.get('service_pk', None)
        # if service_pk:
        #     collab = ProCompany.objects.get(pk=service_pk)
        #     ProCollaborator.objects.create(project=project, collaborator=collab)
        #     return Response(status=status.HTTP_201_CREATED)

    # if request.method == 'DELETE':
    #     pass

    # if request.method == 'PUT':
    #     pass

# @api_view(['POST', 'PUT', 'DELETE'])
# def assignments(request: Request, project_pk, assignment_pk=None):
#     project = Project.objects.get_user_projects(request.user, project_pk)

