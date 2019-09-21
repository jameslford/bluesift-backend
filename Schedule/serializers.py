from typing import Dict
from .models import ProjectTask, ProductAssignment



def serialize_task(task: ProjectTask) -> Dict[str, any]:
    return {
        'name': task.name,
        'assigned_to': task.collaborator(),
        'assigned_product': {
            'name': task.name,
            'pk': task.product.pk
            },
        'start_date': task.start_date,
        'duration': task.duration,
        'children': [serialize_task(child) for child in task.children.all()],
        'predecessor': task.predecessor
    }


def serializer_product_assignment(assignment: ProductAssignment) -> Dict[str, any]:
    product = assignment.product
    return {
        'pk': assignment.pk,
        'name': assignment.name,
        'quantity': assignment.quantity_needed,
        'product': {
            'pk': product.pk,
            'name': f'{product.manufacturer.name}, {product.manu_collection}, {product.manufacturer_style}'
            }
        }
