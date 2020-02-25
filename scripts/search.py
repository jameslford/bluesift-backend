from typing import List
from django.db import transaction
from Search.models import SearchIndex
from SpecializedProducts.models import FinishSurface
# from Products.models import Product
# from Suppliers.models import SupplierLocation

@transaction.atomic
def create_indexes():
    all_si = SearchIndex.objects.all()
    all_si.delete()
    all_fs: List[FinishSurface] = FinishSurface.objects.all()
    for fin in all_fs:
        name = fin.get_name()
        hash_tag = fin.tags()
        tag = list(set(hash_tag))
        tag = '$*'.join(tag)
        qstring = 'product-detail/' + str(fin.pk)
        SearchIndex.objects.create(
            name=name,
            hash_values=tag,
            return_url=qstring
            )


