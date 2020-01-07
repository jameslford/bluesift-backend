"""
serializers used for return project and retailer locations list to user library
"""

# from rest_framework import serializers
from typing import Dict
from django.db.models import Min, Max, F, Sum, DateTimeField
from Addresses.serializers import AddressSerializer
from Products.models import Product
from Retailers.models import RetailerProduct
from .models import ProjectTask, ProductAssignment, BaseProject, Bid
DAY = 60*60*24*1000

def serialize_product(product: Product) -> Dict[str, any]:
    return {
        'pk': product.pk,
        'category': type(product).__name__,
        'unit': product.unit,
        'manufacturer_style': product.manufacturer_style,
        'manu_collection': product.manu_collection,
        'manufacturer_sku': product.manufacturer_sku,
        'name': product.name,
        'swatch_url': product.swatch_image.url if product.swatch_image else None,
        'manufacturer__label': product.manufacturer.label,
        'low_price': getattr(product, 'low_price', None)
        }


def serialize_project_list(project):
    min_date = ProjectTask.objects.filter(project=project).aggregate(Min('start_date'))
    min_date = min_date.get('start_date__min')
    max_date = ProjectTask.objects.filter(project=project).aggregate(max_date=Max(
        F('start_date') + F('duration'), output_field=DateTimeField('day')))
    max_date = max_date.get('max_date')
    assignments = [assi.mini_serialize().get('cost', 0) for assi in project.product_assignments.all()]
    print(assignments)
    additional_costs = project.additional_costs.aggregate(Sum('amount'))
    additional_costs = additional_costs.get('amount__sum')
    bid_sum = Bid.objects.filter(project=project, accepted=True).aggregate(Sum('amount'))
    bid_sum = bid_sum.get('amount__sum')
    return {
        'pk': project.pk,
        'name': project.nickname,
        'deadline': project.deadline,
        'min_date': min_date,
        'max_date': max_date,
        'additional_cost': additional_costs,
        'bid_sum': bid_sum,
        'material_cost': sum(assignments)
        }


def serialize_project_detail(project: BaseProject):
    assignments = serialize_assignments(project)
    tasks = [serialize_task(task) for task in ProjectTask.objects.prefetch_related(
        'children',
        'children__children'
        ).filter(project=project, level=0)]
    return {
        'pk' : project.pk,
        'image' : project.image.url if project.image else None,
        'nickname' : project.nickname,
        'deadline' : project.deadline,
        'address' : AddressSerializer(project.address).data,
        'product_count' : project.product_count(),
        'assignments': assignments,
        'tasks': tasks
        }


def serialize_assignments(project: BaseProject):
    assignments = ProductAssignment.objects.filter(project=project).values(
        'product_id',
        'pk',
        'name',
        'procured',
        'supplier',
        'supplier_product',
        'quantity_needed'
        )
    assignments = list(assignments)
    product_ids = [assi['product_id'] for assi in assignments]
    products = Product.subclasses.select_related(
        'manufacturer').filter(pk__in=product_ids).select_subclasses()
    products = [serialize_product(prod) for prod in products]
    suppliers = RetailerProduct.objects.select_related(
        'retailer',
        'retailer__address'
        ).filter(product__pk__in=product_ids).values(
            'pk',
            'product_id',
            'retailer__nickname',
            'in_store_ppu',
            'retailer__pk',
            'units_available_in_store',
            'lead_time_ts',
        )
    for assignment in assignments:
        assignment['suppliers'] = [sup for sup in suppliers if sup['product_id'] == assignment['product_id']]
        # pylint: disable=cell-var-from-loop
        prod = list(filter(lambda x: x['pk'] == assignment.get('product_id'), products))
        assignment['product'] = prod[0] if prod else None
    return assignments

def serialize_task(task: ProjectTask) -> Dict[str, any]:
    return {
        'pk': task.pk,
        'name': task.name,
        'assigned_product': {
            'name': task.product.name,
            'pk': task.product.pk} if task.product else None,
        'progress': task.progress,
        'saved': True,
        'start_date': task.start_date,
        'duration': task.duration / DAY if task.duration else None,
        'children': [serialize_task(child) for child in task.children.all()],
        'predecessor': serialize_task(task.predecessor) if task.predecessor else None
    }


def reserialize_task(project, data, parent: ProjectTask = None):
    task_pk = data.get('pk', None)
    children = data.get('children', [])
    changed = data.get('changed', False)
    new = False
    if task_pk:
        task: ProjectTask = ProjectTask.objects.get(pk=task_pk)
    else:
        new = True
        task = ProjectTask()
        task.project = project
    if changed or new:
        task.name = data.get('name', task.name)
        task.duration = data.get('duration', task.duration)
        task.start_date = data.get('start_date', task.start_date)
        task.progress = data.get('progress', task.progress)
        product_pk = None
        try:
            product_pk = data['assigned_product']['pk']
        except (KeyError, TypeError):
            pass
        if product_pk:
            product = project.product_assignments.get(pk=product_pk)
            task.product = product
        if parent:
            task.parent = parent
        task.save()
    for child in children:
        reserialize_task(project, child, task)





# def serialize_collaborators(project: BaseProject):
#     pros = ProCollaborator.select_related().objects.filter(project=project).values(
#         'collaborator',
#         'collaborator__service__label',
#         'collaborator__name',
#         'role'
#         )





# def project_serializer(project: BaseProject):
#     return {
#         'pk' : project.pk,
#         'image' : project.image.url if project.image else None,
#         'nickname' : project.nickname,
#         'deadline' : project.deadline,
#         'address' : AddressSerializer(project.address).data,
#         'product_count' : project.product_count(),
#         # 'tasks': []
#         }

# def project_full_serializer(project: BaseProject):
#     tasks = ProjectTask.objects.prefetch_related(
#         'children',
#         'children__children'
#     ).select_related(
#         'product',
#         'pro_collaborator',
#         'user_collaborator'
#         ).filter(project=project)
#     # assignments = ProductAssignment.objects.select_related(
#     # 'product',
#     # 'supplier',
#     # 'supplier_product__product'
#     # ).filter(project=project)

#     project_product_pks = project.products.all().values_list('product__pk', flat=True)
#     products = Product.subclasses.prefetch_related(
#         'priced',
#         'priced__retailer'
#         ).select_related('manufacturer').filter(pk__in=project_product_pks).select_subclasses()
#     res = []
#     for kls in ProductSubClass.__subclasses__():
#         kls_res = {
#             'name': kls.__name__,
#             'products': [serialize_product_priced(product) for product in products if isinstance(product, kls)]
#             }
#         res.append(kls_res)
#     assignments = ProductAssignment.objects.select_related(
#         'product__manufacturer',
#         'supplier',
#         'supplier_product',
#         ).filter(project=project)
#     # assignments = project.product_assignments.select_related(
#     #     'product',
#     #     'product__manufacturer'
#     #     ).all()
#     response = {
#         'assignments': [serialize_product_assignment(assi) for assi in assignments],
#         'categories': [cat.__name__ for cat in ProductSubClass.__subclasses__()],
#         'groups': res
#         }

#     return {
#         'pk' : project.pk,
#         'image' : project.image.url if project.image else None,
#         'nickname' : project.nickname,
#         'deadline' : project.deadline,
#         'address' : AddressSerializer(project.address).data,
#         'product_count' : project.product_count(),
#         'tasks': [serialize_task(task) for task in tasks],
#         # 'assignments': [serializer_product_assignment(assi) for assi in assignments]
#         # 'assignments': [assi.mini_serialize() for assi in assignments]
#         'assignments': response
#     }

# def project_mini_serializer(project: BaseProject):
#     tasks = ProjectTask.objects.prefetch_related(
#         'children',
#         'children__children'
#         ).select_related(
#             'pro_collaborator',
#             'user_collaborator'
#             ).filter(project=project, level=0)
#     assignments = ProductAssignment.objects.select_related(
#         'product',
#         'supplier',
#         'supplier_product'
#         ).filter(project=project)
#     return {
#         'pk' : project.pk,
#         'image' : project.image.url if project.image else None,
#         'nickname' : project.nickname,
#         'deadline' : project.deadline,
#         'address' : AddressSerializer(project.address).data,
#         'product_count' : project.product_count(),
#         'tasks': [task.mini_serialize() for task in tasks],
#         'assignments': [assi.mini_serialize() for assi in assignments]
#         }





# def serialize_product_assignment(assignment: ProductAssignment) -> Dict[str, any]:

#     priced_products = serialize_product_priced(assignment.product)
#     supplier = None
#     # if a supplier is already assigned to the product assignment, find corresponsing retilaer product
#     if assignment.supplier:
#         supplier = assignment.supplier.products.filter(product__pk=assignment.product.pk).first()
#         if supplier:
#             supplier = supplier.get_priced()

#     return {
#         'pk': assignment.pk,
#         'name': assignment.name,
#         'quantity': assignment.quantity_needed,
#         'product': priced_products,
#         'procured': assignment.procured,
#         'supplier': supplier
#         }
