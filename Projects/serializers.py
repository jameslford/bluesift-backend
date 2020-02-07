"""
serializers used for return project and retailer locations list to user library
"""

from typing import Dict
from Addresses.serializers import AddressSerializer
# from Products.serializers import serialize_product_priced
from Products.serializers import serialize_product
from .models import ProjectTask, Project, ProjectProduct
DAY = 60*60*24*1000



def serialize_project_detail(project: Project):
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
        'tasks': tasks
        }


def serialize_task(task: ProjectTask) -> Dict[str, any]:
    return {
        'pk': task.pk,
        'name': task.name,
        'progress': task.progress,
        'saved': True,
        'start_date': task.start_date,
        'duration': task.duration / DAY if task.duration else None,
        'children': [serialize_task(child) for child in task.children.all()],
        'predecessor': serialize_task(task.predecessor) if task.predecessor else None
    }
        # 'assigned_product': {
        #     'name': task.product.name,
        #     'pk': task.product.pk
        #     } if task.product else None,
        # 'selected_retailer': task.selected_retailer.pk if task.selected_retailer else None,
        # 'supplier_product': task.supplier_product.pk if task.supplier_product else None,
        # 'product': serialize_product_priced(task.product) if task.product else None,


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


def resource_serializer(product: ProjectProduct):
    return {
        'pk': product.pk,
        'linked_tasks': {'pk': product.linked_tasks.pk, 'name': product.linked_tasks.name} if product.linked_tasks else None,
        'quantity': product.quantity_needed,
        'procured': product.procured,
        'supplier_product': product.supplier_product.get_priced() if product.supplier_product else None,
        'product': serialize_product(product.product.product),
        'priced': [pro.get_priced() for pro in product.product.product.priced.all()]
    }
