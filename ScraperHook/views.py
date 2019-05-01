import requests
from rest_framework.decorators import (
    api_view,
    permission_classes
    )
from rest_framework.response import Response


@api_view(['GET'])
def scraper_dashboard(request):
    url = 'http://bluesift-scraper.herokuapp.com/home/dashboard'
    response = requests.get(url).json()
    return Response(response)
