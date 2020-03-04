from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from django.contrib.postgres.search import TrigramSimilarity
from django.db.models.functions import Concat
from django.db.models.fields import CharField
from django.db.models.query import QuerySet, Value, F
from Suppliers.models import SupplierLocation
from Products.models import Product
from .models import SearchIndex

# Create your views here.
@api_view(['GET'])
def search(request: Request):
    # qdict = request.GET.urlencode()
    query = request.query_params.get('search')
    # ret = SearchIndex.objects.filter(hash_value__icontains=query).values('name', 'return_url')[0:10]
    cats = SearchIndex.objects.annotate(
        similarity=TrigramSimilarity('hash_value', query),
        ).filter(similarity__gte=0.1).order_by('-similarity').values('name', 'return_url', 'similarity')[0:8]
        
    sups = SupplierLocation.objects.annotate(
        return_url=Concat(Value('business-detail/'), 'pk', output_field=CharField()),
        in_department=Value('supplier'),
        name=F('nickname'),
        similarity=TrigramSimilarity('hash_value', query),
        ).filter(similarity__gte=0.1).order_by('-similarity').values('name', 'return_url', 'in_department', 'similarity')[0:8]

    prods = Product.objects.annotate(
        return_url=Concat(Value('product-detail/'), 'pk', output_field=CharField()),
        in_department=Value('product'),
        name=F('name'),
        similarity=TrigramSimilarity('hash_value', query),
        ).filter(similarity__gte=0.1).order_by('-similarity').values('name', 'return_url', 'in_department', 'similarity')[0:8]

    return Response(cats)


@api_view(['GET'])
def full_search(request: Request):
    query = request.query_params.get('search')
