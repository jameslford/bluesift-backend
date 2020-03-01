from django.core.management.base import BaseCommand
from scripts.facets import create_facets
from ProductFilter.models import BaseFacet, QueryIndex
from scripts.finish_surfaces import clean_products
# from scripts.search import create_indexes


class Command(BaseCommand):

    def handle(self, *args, **options):
        clean_products()
        facets = BaseFacet.objects.all()
        qis = QueryIndex.objects.all()
        facets.delete()
        qis.delete()
        create_facets()
