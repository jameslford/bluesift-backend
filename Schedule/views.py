from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from Products.models import Product, ProductSubClass
from Products.serializers import serialize_product
from UserProductCollections.models import BaseProject
from .serializers import serialize_task, serializer_product_assignment


@api_view(['GET'])
def tasks(request: Request, project_pk):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)
    tasks = project.tasks.select_related(
        'product',
        'collaborators',
        'pro_collaborators'
    ).all()
    res = [serialize_task(task) for task in tasks]
    return Response(res)


@api_view(['GET'])
def product_assignments(request: Request, project_pk):
    project = BaseProject.objects.get_user_projects(request.user, project_pk)
    project_product_pks = project.products.all().values_list('product__pk', flat=True)
    products = Product.subclasses.select_related('manufacturer').filter(pk__in=project_product_pks).select_subclasses()
    res = []
    categories = [kls for kls in ProductSubClass.__subclasses__()]
    for kls in categories:
        kls_res = {
            'name': kls.__name__,
            'products': [serialize_product(product) for product in products if type(product) == kls]
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
