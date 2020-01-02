"""
serializers used for return project and retailer locations list to user library
"""

# from rest_framework import serializers
from typing import Dict
from Addresses.serializers import AddressSerializer
from Schedule.models import ProjectTask, ProductAssignment
from Products.serializers import serialize_product_priced
from .models import ProjectTask, ProductAssignment, BaseProject
DAY = 60*60*24*1000


def project_serializer(project: BaseProject):
    return {
        'pk' : project.pk,
        'image' : project.image.url if project.image else None,
        'nickname' : project.nickname,
        'deadline' : project.deadline,
        'address' : AddressSerializer(project.address).data,
        'product_count' : project.product_count(),
        # 'tasks': []
        }

def project_full_serializer(project: BaseProject):
    return {
        'pk' : project.pk,
        'image' : project.image.url if project.image else None,
        'nickname' : project.nickname,
        'deadline' : project.deadline,
        'address' : AddressSerializer(project.address).data,
        'product_count' : project.product_count(),
        # 'tasks': []
    }

def project_mini_serializer(project: BaseProject):
    tasks = ProjectTask.objects.prefetch_related(
        'children',
        'children__children'
        ).select_related(
            'pro_collaborator',
            'user_collaborator'
            ).filter(project=project, level=0)
    assignments = ProductAssignment.objects.select_related(
        'product',
        'supplier',
        'supplier_product'
        ).filter(project=project)
    return {
        'pk' : project.pk,
        'image' : project.image.url if project.image else None,
        'nickname' : project.nickname,
        'deadline' : project.deadline,
        'address' : AddressSerializer(project.address).data,
        'product_count' : project.product_count(),
        'tasks': [task.mini_serialize() for task in tasks],
        'assignments': [assi.mini_serialize() for assi in assignments]
        }


def serialize_task(task: ProjectTask) -> Dict[str, any]:
    return {
        'pk': task.pk,
        'name': task.name,
        'assigned_to': task.collaborator(),
        'assigned_product': serializer_product_assignment(task.product) if task.product else None,
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


def serializer_product_assignment(assignment: ProductAssignment) -> Dict[str, any]:

    priced_products = serialize_product_priced(assignment.product)
    supplier = None
    # if a supplier is already assigned to the product assignment, find corresponsing retilaer product
    if assignment.supplier:
        supplier = assignment.supplier.products.filter(product__pk=assignment.product.pk).first()
        if supplier:
            supplier = supplier.get_priced()

    return {
        'pk': assignment.pk,
        'name': assignment.name,
        'quantity': assignment.quantity_needed,
        'product': priced_products,
        'procured': assignment.procured,
        'supplier': supplier
        }
