from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from Products.models import Product, ProductSubClass
from Products.serializers import serialize_product_priced
from UserProductCollections.models import BaseProject
from Groups.models import ProCompany
from .models import ProductAssignment, ProCollaborator
from .serializers import serializer_product_assignment, serialize_task, reserialize_task


@api_view(['GET', 'POST', 'DELETE'])
def tasks(request: Request, project_pk, task_pk=None):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)

    if request.method == 'GET':
        p_tasks = project.tasks.select_related(
            'product',
            'user_collaborator',
            'pro_collaborator'
        ).filter(level=0)
        res = [serialize_task(task) for task in p_tasks]
        if not res:
            res = [{
                'name': 'New Major Task',
                'children': []
            }]
        assignments = project.product_assignments.select_related(
            'product',
            'product__manufacturer'
            ).all()
        project_node = {
            'assignments': [serializer_product_assignment(assi) for assi in assignments],
            'project_name': project.nickname,
            'project_deadline': project.deadline,
            'tasks': res
            }
        return Response(project_node)

    if request.method == 'POST':
        data = request.data
        if data.get('project_changed', False):
            project.nickname = data.get('project_name', project.nickname)
            project.deadline = data.get('project_deadline', project.deadline)
            project.save()
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


@api_view(['GET'])
def product_assignments(request: Request, project_pk):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)
    project_product_pks = project.products.all().values_list('product__pk', flat=True)
    products = Product.subclasses.prefetch_related(
        'priced',
        'priced__retailer'
        ).select_related('manufacturer').filter(pk__in=project_product_pks).select_subclasses()
    res = []
    categories = [kls for kls in ProductSubClass.__subclasses__()]
    for kls in categories:
        kls_res = {
            'name': kls.__name__,
            'products': [serialize_product_priced(product) for product in products if isinstance(product, kls)]
            }
        res.append(kls_res)
    assignments = project.product_assignments.select_related(
        'product',
        'product__manufacturer'
        ).all()
    response = {
        'assignments': [serializer_product_assignment(assi) for assi in assignments],
        'categories': [cat.__name__ for cat in categories],
        'groups': res
        }
    return Response(response)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def collabsForService(request: Request, service_pk: int):
    projects = request.user.get_collections()
    pro_collab = ProCollaborator.objects.filter(collaborator__pk=service_pk).values_list('project__pk', flat=True)
    print('pro collab = ', list(pro_collab))
    return Response(
        [{'nickname': proj.nickname, 'pk': proj.pk, 'remove': proj.pk in pro_collab} for proj in projects],
        status=status.HTTP_200_OK)


@api_view(['GET', 'POST', 'DELETE', 'PUT'])
@permission_classes((IsAuthenticated,))
def collaborators(request: Request, project_pk=None):

    if request.method == 'GET':
        project = BaseProject.objects.get_user_projects(request.user, project_pk)
        pro_collabs = project.pro_collaborators.all().select_related('collaborator', 'contact', 'contact__user')
        user_collabs = project.collaborators.all().select_related('collaborator')
        return Response({
            'pro_collaborators': [col.serialize() for col in pro_collabs],
            'user_collaborators': [col.serialize() for col in user_collabs]
        }, status=status.HTTP_200_OK)

    if request.method == 'POST':
        project = BaseProject.objects.get_user_projects(request.user, project_pk)
        service_pk = request.data.get('service_pk', None)
        if service_pk:
            collab = ProCompany.objects.get(pk=service_pk)
            ProCollaborator.objects.create(project=project, collaborator=collab)
            return Response(status=status.HTTP_201_CREATED)



@api_view(['POST', 'PUT', 'DELETE'])
def assignment_cud(request: Request, project_pk, assignment_pk=None):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)

    if request.method == 'POST':
        ProductAssignment.objects.update_assignments(project, *request.data)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == 'DELETE':
        assignment = project.product_assignments.get(pk=assignment_pk)
        assignment.delete()
        return Response('deleted')

    # if request.method == 'PUT':
    #     assignment = project.assignments.filter(pk=assignment_pk)


    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
