from django.db import transaction
from FinishSurfaces.models import FinishSurface


@transaction.atomic()
def assign_shape():
    pass