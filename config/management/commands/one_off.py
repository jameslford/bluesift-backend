from django.core.management.base import BaseCommand
# from utils.images import remove_background
from scripts.finish_surfaces import assign_tiling_image
from SpecializedProducts.models import FinishSurface

class Command(BaseCommand):

    def handle(self, *args, **options):

        p1 = FinishSurface.objects.filter(manufacturer__label__iexact='crossville')
        p2 = FinishSurface.objects.filter(walls=True)
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



