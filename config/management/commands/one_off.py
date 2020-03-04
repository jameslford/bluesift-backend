from typing import List
from django.core.management.base import BaseCommand
from SpecializedProducts.models import FinishSurface
from Products.models import Manufacturer
# from utils.images import remove_background
# from scripts.finish_surfaces import assign_tiling_image
# from SpecializedProducts.models import FinishSurface
# from scripts.search import create_indexes
# from scripts.finish_surfaces import default_clean
from scripts.facets import create_facets
from Scraper.models import ScraperGroup
from config.models import ConfigTree

class Command(BaseCommand):

    def handle(self, *args, **options):
        ConfigTree.refresh()
        # range = ScraperGroup.objects.get(manufacturer__label__iexact='viking')
        # range.scrape()
        # cache.clear()

        # create_facets()
        # default_clean()
        # all_fs: List[FinishSurface] = FinishSurface.subclasses.select_related('manufacturer').all().select_subclasses()
        # for fin in all_fs:
        #     fin.assign_name()
        # create_indexes()
        # p1 = FinishSurface.objects.filter(manufacturer__label__iexact='crossville')
        # p2 = FinishSurface.objects.filter(walls=True)
        # prods = FinishSurface.objects.all().reverse()
        # num = 0
        # for prod in prods:
        #     print(num)
        #     print(prod.bb_sku)
        #     assign_tiling_image(prod)
        #     num += 1


        # products = Product.subclasses.all().select_subclasses()
        # products = Product.subclasses.filter().select_subclasses()
        # print(products.query)
        # remove_background()



