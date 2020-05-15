from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from rest_framework.request import Request
from django.core.cache import cache
from django.db import models
from django.db.models.functions import TruncDate
from django.contrib.auth import get_user_model
from Scraper.models import ScraperGroup
from config.models import ConfigTree
from scripts.scrapers import create_scrapers
from ProductFilter.models import BaseFacet, QueryIndex
from Suppliers.models import SupplierProduct
from Analytics.models import GenericRecord
from Projects.models import Project
from Products.models import Product
from scripts.suppliers import refresh_supplier_products
from scripts.generate_data import delete_fake

# from scripts.finish_surfaces import clean_products
from .tasks import create_indexes

# from django.contrib.contenttypes.models import ContentType


@api_view(["GET"])
@permission_classes((IsAdminUser,))
def dashboard(request: Request):

    user_model = get_user_model()
    demo_reg_users = user_model.objects.filter(demo=True, is_supplier=False).count()
    reg_users = user_model.objects.filter(demo=False, is_supplier=False).count()
    demo_sup_users = user_model.objects.filter(demo=True, is_supplier=True).count()
    sup_users = user_model.objects.filter(demo=False, is_supplier=True).count()
    projects = Project.objects.all().count()
    supplier_products = SupplierProduct.objects.all().count()
    products = Product.objects.all().count()

    views = (
        GenericRecord.objects.all()
        .annotate(date=TruncDate("recorded"))
        .values("date")
        .annotate(count=models.Count("id"))
        .values("count", "date")
        .order_by("date")
    )

    res_dict = {
        "demo_reg_users": demo_reg_users,
        "reg_users": reg_users,
        "demo_sup_users": demo_sup_users,
        "sup_users": sup_users,
        "projects": projects,
        "supplier_products": supplier_products,
        "products": products,
        "views": views,
    }
    return Response(res_dict, status=status.HTTP_200_OK)


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
        return Response(status=status.HTTP_200_OK)
    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET"])
@permission_classes((IsAdminUser,))
def refresh_search(request):
    create_indexes.delay()
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((IsAdminUser,))
def refresh_supplier_employees(request):
    pass


@api_view(["GET", "DELETE"])
@permission_classes((IsAdminUser,))
def demo(request):
    if request.method == "GET":
        refresh_supplier_products()
        return Response(status=status.HTTP_201_CREATED)

    if request.method == "DELETE":
        delete_fake()
        return Response(status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["GET", "DELETE"])
@permission_classes((IsAdminUser,))
def clean_scraper_group(request, pk):
    scraper: ScraperGroup = ScraperGroup.objects.get(pk=pk)
    scraper.clean_products()
    return Response(status=status.HTTP_200_OK)
