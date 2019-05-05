import os
import requests
from django.conf import settings
from rest_framework.decorators import (
    api_view,
    permission_classes
    )
from rest_framework.response import Response
from .permissions import ScraperHookPermissions

BASE_URL = 'http://bluesift-scraper.herokuapp.com'


def get_header():
    header = {'authorization': os.environ.get('SCRAPER_AUTH_HEADER', None)}
    if settings.ENVIRONMENT == 'local':
        header = {'authorization': settings.SCRAPER_AUTH_HEADER}
    return header

# dashboard presentation

@api_view(['GET'])
@permission_classes((ScraperHookPermissions,))
def scraper_dashboard(request):

    """ gets data presentation for scraper dashboard """

    url = BASE_URL + '/home/dashboard'
    response = requests.get(url, headers=get_header()).json()
    return Response(response)

# button triggers to receive

@api_view(['POST'])
@permission_classes((ScraperHookPermissions,))
def get_data_from_scraper(request):
    #check to make sure all existing bb_skus are on list
    pass


@api_view(['POST'])
@permission_classes((ScraperHookPermissions,))
def send_to_production(request):
    pass


# receiving functions

@api_view(['POST'])
@permission_classes((ScraperHookPermissions,))
def scraper_data_input(request):
    pass

@api_view(['POST'])
@permission_classes((ScraperHookPermissions,))
def production_input(request):
    pass
