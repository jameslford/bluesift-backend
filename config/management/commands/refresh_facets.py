from django.core.management.base import BaseCommand
from scripts.facets import create_facets
from ProductFilter.models import BaseFacet, QueryIndex, FacetOthersCollection
# from scripts.search import create_indexes


class Command(BaseCommand):

    def handle(self, *args, **options):
        facets = BaseFacet.objects.all()
        ocs = FacetOthersCollection.objects.all()
        qis = QueryIndex.objects.all()
        facets.delete()
        ocs.delete()
        qis.delete()
        create_facets()
