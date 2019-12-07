from django.db import transaction


@transaction.atomic()
def assign_shape():
    pass