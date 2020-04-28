from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from django.core.cache import cache
from Scraper.models import ScraperGroup
from config.models import ConfigTree
from scripts.scrapers import create_scrapers
from Products.models import Product
from ProductFilter.models import BaseFacet, QueryIndex
from scripts.finish_surfaces import clean_products

# from django.contrib.contenttypes.models import ContentType


@api_view(["GET"])
@permission_classes((IsAdminUser,))
def dashboard(request: Request):
    pass


@api_view(["GET", "POST", "PUT", "DELETE"])
@permission_classes((IsAdminUser,))
def scrape(request: Request, pk=None):

    if request.method == "POST":
        data = request.data
        scraper_pk = data.get("scraper_pk")
        scraper: ScraperGroup = ScraperGroup.objects.get(pk=scraper_pk)
        scraper.scrape()
        return Response(scraper.response(), status=status.HTTP_200_OK)

    if request.method == "GET":
        scrapers = ScraperGroup.objects.select_related("manufacturer").all()
        scrapers = [scrap.response() for scrap in scrapers]
        return Response(scrapers, status=status.HTTP_200_OK)

    if request.method == "PUT":
        create_scrapers()
        scrapers = ScraperGroup.objects.select_related("manufacturer").all()
        scrapers = [scrap.response() for scrap in scrapers]
        return Response(scrapers, status=status.HTTP_200_OK)

    if request.method == "DELETE":
        scraper = ScraperGroup.objects.get(pk=pk)
        scraper.delete()
        scrapers = ScraperGroup.objects.select_related("manufacturer").all()
        scrapers = [scrap.response() for scrap in scrapers]
        return Response(scrapers, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET", "POST"])
@permission_classes((IsAdminUser,))
def refresh_tree(request):

    if request.method == "GET":
        tree = ConfigTree.load()
        res = {
            "product_tree": tree.product_tree,
            "supplier_tree": tree.supplier_tree,
            "last_refreshed": tree.last_refreshed,
        }
        return Response(res, status=status.HTTP_200_OK)

    if request.method == "POST":
        ConfigTree.refresh()
        tree = ConfigTree.load()
        res = {
            "product_tree": tree.product_tree,
            "supplier_tree": tree.supplier_tree,
            "last_refreshed": tree.last_refreshed,
        }
        return Response(res, status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET", "POST"])
@permission_classes((IsAdminUser,))
def get_final_images(request, pk):

    group: ScraperGroup = ScraperGroup.objects.get(pk=pk)
    group.get_final_images()
    return Response(group.response(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAdminUser,))
def convert_geometries(request, pk):
    group: ScraperGroup = ScraperGroup.objects.get(pk=pk)
    group.convert_geometries()
    return Response(group.response(), status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAdminUser,))
def refresh_facets(request):
    if request.method == "GET":
        cache.clear()
        facets = BaseFacet.objects.all()
        qis = QueryIndex.objects.all()
        facets.delete()
        qis.delete()
        tree: ConfigTree = ConfigTree.load()
        tree = tree.refresh()
        # prods = [Product] + Product.__subclasses__()
        # print(prods)
        # for prod in prods:
        #     prod.create_facets()
        return Response(status=status.HTTP_200_OK)
