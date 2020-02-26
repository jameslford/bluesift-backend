from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from django.contrib.postgres.search import TrigramSimilarity
from .models import SearchIndex

# Create your views here.
@api_view(['GET'])
def search(request: Request):
    # qdict = request.GET.urlencode()
    query = request.query_params.get('search')
    # ret = SearchIndex.objects.filter(hash_value__icontains=query).values('name', 'return_url')[0:10]
    ret = SearchIndex.objects.annotate(
        similarity=TrigramSimilarity('hash_value', query),
        ).filter(similarity__gte=0.1).order_by('-similarity').values('name', 'return_url', 'in_department', 'hash_value', 'similarity')[0:10]
    return Response(ret)
