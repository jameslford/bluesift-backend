from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from Scraper.models import ScraperGroup
from config.models import ConfigTree
from scripts.scrapers import create_scrapers


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def dashboard(request: Request):
    pass


@api_view(['GET', 'POST', 'PUT'])
@permission_classes((IsAdminUser,))
def scrape(request: Request):

    if request.method == 'POST':
        data = request.data
        scraper_pk = data.get('pk')
        scraper: ScraperGroup = ScraperGroup.objects.get(pk=scraper_pk)
        scraper.scrape()
        return Response(scraper.response(), status=status.HTTP_200_OK)

    if request.method == 'GET':
        scrapers = ScraperGroup.objects.select_related('manufacturer').all()
        scrapers = [scrap.response() for scrap in scrapers]
        return Response(scrapers, status=status.HTTP_200_OK)

    if request.method == 'PUT':
        create_scrapers()
        scrapers = ScraperGroup.objects.select_related('manufacturer').all()
        scrapers = [scrap.response() for scrap in scrapers]
        return Response(scrapers, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def refresh_tree(request):
    ConfigTree.refresh()


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def product_groups(request):
    pass
