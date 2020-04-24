from typing import List
import datetime
import random
from django.utils import timezone
from django.core.management.base import BaseCommand
from django.core.cache import cache
from SpecializedProducts.models import FinishSurface
from Products.models import Manufacturer
# from utils.images import remove_background
# from scripts.finish_surfaces import assign_tiling_image
# from SpecializedProducts.models import FinishSurface
from scripts.search import create_indexes
# from scripts.finish_surfaces import default_clean
from scripts.facets import create_facets
from Scraper.models import ScraperGroup
from config.models import ConfigTree, UserTypeStatic
from Search.models import SearchIndex
from scripts.demo_data import create_parent_tasks, create_child_tasks, add_task_products
from Projects.models import ProjectTask, Project, ProjectProduct
from SpecializedProducts.models import Appliance, Cooking, Range
from Suppliers.models import SupplierLocation
from Analytics.models import SupplierProductListRecord

def get_dates(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + datetime.timedelta(days=n)

def partition(nlist, n):
    last = 0
    groups = []
    for i in range(n):
        count = random.randint(last, last + 20)
        try:
            print(last, count)
            groups.append(nlist[last: count])
            last = count + 1
            # print(groups)
        except IndexError:
            continue
    return groups





    # return [nlist[i::n] for i in range(n)]


class Command(BaseCommand):

    def handle(self, *args, **options):
        uts = UserTypeStatic.objects.all()

        for ut in uts:
            ut.create_img()
        # for rangen in Range.objects.all():
        #     print(rangen.name)
        # pass
        # cache.clear()
        # cooking = Cooking.objects.all()
        # for cook in cooking:
        #     if not cook.manufacturer_sku:
        #         cook.delete()
        # orgs = Cooking.objects.all()
        # for org in orgs:
        #     nrange = Range(cooking_ptr_id=org.pk)
        #     nrange.__dict__.update(org.__dict__)
        #     nrange.save()
        # for supplier in SupplierLocation.objects.all():
        #     startdate = timezone.now() - datetime.timedelta(days=30)
        #     enddate = timezone.now()
        #     records = SupplierProductListRecord.objects.filter(
        #         supplier=supplier
        #         ).values_list('pk', flat=True)
        #     print(len(records))
        #     rgroups = partition(list(records), 30)
        #     print(rgroups)
        #     # last = 0
        #     for date, group in zip(get_dates(startdate, enddate), rgroups):
        #         # print(date, group)
        #         cords = SupplierProductListRecord.objects.filter(
        #             supplier=supplier,
        #             pk__in=group
        #             )
        #         cords.update(recorded=date)
                # views = random.randint(5, 40)
                # if records[last: views]:
                #     for record in records[last:views]:
                #         record.recorded = date
                #         record.save()
                #         last += views
                    # records[last: views].update(
                    #     recorded=dat
                    # )
                # for count in range(0, views):

            # dates = timezone.now() + datetime.timedelta
        # projects = Project.objects.all()
        # for project in projects:
        #     project.deadline = datetime.date(2020, 4, 10)
        #     project.save()
        # pprods = ProjectProduct.objects.all()
        # for p in pprods:
        #     p.delete()
        # projects = Project.objects.all()
        # for project in projects:
        #     project.deadline = timezone.now() + datetime.timedelta(days=random.randint(20, 40))
        #     project.save()
        #     tasks = project.tasks.all()
        #     products = project.owner.products.all()
        #     for task, product in zip(tasks, products):
        #         prod = ProjectProduct.objects.create(linked_tasks=task, product=product)
        #         prod.quantity_needed = random.randint(10, 100)
        #         if random.randint(0, 10) > 6:
        #             prod.supplier_product = prod.product.product.priced.first()
        #             prod.procured = random.choice([True, False])
        #         prod.save()
        # tasks = ProjectTask.objects.all()
        # for task in tasks:
        #     task.save()
        # tasks.delete()
        # create_parent_tasks()
        # create_child_tasks()
        # add_task_products()
