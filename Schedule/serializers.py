from typing import Dict
from Products.serializers import serialize_product_priced
from .models import ProjectTask, ProductAssignment

def serialize_task(task: ProjectTask) -> Dict[str, any]:
    return {
        'pk': task.pk,
        'name': task.name,
        'assigned_to': task.collaborator(),
        'assigned_product': serializer_product_assignment(task.product) if task.product else None,
        'start_date': task.start_date,
        'duration': task.duration,
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
    return {
        'pk': assignment.pk,
        'name': assignment.name,
        'root': False,
        'quantity': assignment.quantity_needed,
        'product': serialize_product_priced(assignment.product),
        'supplier': {
            'pk': assignment.supplier.pk,
            'name': assignment.supplier.nickname
            }
        }
