from typing import Dict
from Products.serializers import serialize_product_priced
from .models import ProjectTask, ProductAssignment

def serialize_task(task: ProjectTask) -> Dict[str, any]:
    return {
        'name': task.name,
        'assigned_to': task.collaborator(),
        'assigned_product': serializer_product_assignment(task.product),
        'start_date': task.start_date,
        'duration': task.duration,
        'children': [serialize_task(child) for child in task.children.all()],
        'predecessor': serialize_task(task.predecessor)
    }


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
