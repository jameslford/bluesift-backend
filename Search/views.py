import functools
import operator
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from django.contrib.postgres.search import TrigramSimilarity
from django.contrib.postgres.search import SearchQuery, SearchVector, SearchRank
from django.db.models.functions import Concat
from django.db.models.fields import CharField, UUIDField
from django.db.models.query import QuerySet, Value, F
from Suppliers.models import SupplierLocation
from Products.models import Product
from .models import SearchIndex

@api_view(['GET'])
def search(request: Request):
    count = SearchIndex.objects.all()
    print(count.count())
    query = request.query_params.get('search')
    vector = SearchVector('hash_value')
    sios = SearchIndex.objects.annotate(
        similarity=SearchRank(vector, query)
        ).order_by('-similarity').filter(similarity__gte=0.04).values(
            'name',
            'return_url',
            'hash_value',
            'in_department',
            'similarity'
        )[0:6]
    sios = list(sios)
    if not sios or len(sios) < 6:
        res = SearchIndex.objects.annotate(
            similarity=TrigramSimilarity('hash_value', query),
            ).filter(similarity__gte=0.1).order_by('-similarity').values(
                'name',
                'return_url',
                'hash_value',
                'in_department',
                'similarity'
                )[0:8]

        sios = sios + list(res)

    return Response(sios)

 

@api_view(['GET'])
def full_search(request: Request):
    query = request.query_params.get('search')
