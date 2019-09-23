from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from Products.models import Product, ProductSubClass
from Products.serializers import serialize_product_priced
from UserProductCollections.models import BaseProject
from .serializers import serialize_task, serializer_product_assignment
from .models import ProductAssignment


@api_view(['GET'])
def tasks(request: Request, project_pk):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)
    p_tasks = project.tasks.select_related(
        'product',
        'user_collaborator',
        'pro_collaborator'
    ).all()
    res = [serialize_task(task) for task in p_tasks]
    project_node = [{
        'name': project.nickname,
        'root': True,
        'children': res
        }]
    return Response(project_node)


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
            'products': [serialize_product_priced(product) for product in products if type(product) == kls]
            }
        res.append(kls_res)
    assignments = project.product_assignments.select_related(
        'product',
        'product__manufacturer'
        ).all()
    response = {
        'assignments':[serializer_product_assignment(assi) for assi in assignments],
        'categories': [cat.__name__ for cat in categories],
        'groups': res
        }
    return Response(response)



@api_view(['GET'])
def collaborators(request: Request, project_pk):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)
    pass


@api_view(['POST', 'PUT', 'DELETE'])
def assignment_cud(request: Request, project_pk, assignment_pk=None):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)

    if request.method == 'POST':
        assignment = ProductAssignment.objects.create_assignment(project, **request.data)
        return Response(serializer_product_assignment(assignment))

    if request.method == 'DELETE':
        assignment = project.product_assignments.get(pk=assignment_pk)
        assignment.delete()
        return Response('deleted')
