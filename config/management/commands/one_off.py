from typing import List
import datetime
import random
from django.core.management.base import BaseCommand
from SpecializedProducts.models import FinishSurface
from Products.models import Manufacturer
# from utils.images import remove_background
# from scripts.finish_surfaces import assign_tiling_image
# from SpecializedProducts.models import FinishSurface
from scripts.search import create_indexes
# from scripts.finish_surfaces import default_clean
from scripts.facets import create_facets
from Scraper.models import ScraperGroup
from config.models import ConfigTree
from Search.models import SearchIndex
from scripts.demo_data import create_parent_tasks, create_child_tasks
from Projects.models import ProjectTask, Project

from SpecializedProducts.models import Appliance


class Command(BaseCommand):

    def handle(self, *args, **options):
        # projects = Project.objects.all()
        # for project in projects:
        #     project.deadline = datetime.date(2020, 4, 10)
        #     project.save()
        tasks = ProjectTask.objects.all()
        # tasks.delete()
        # create_parent_tasks()
        # create_child_tasks()
        for task in tasks:
            task.save()
        # create_child_tasks()
        # projects = Project.objects.all()
        # for project in projects:

        #     tasks = list(project.tasks.filter(level=0))
        #     parent_task = tasks.pop(0)
        #     # date = parent_task.start_date + datetime.timedelta(days=random.randint(3, 9))
        #     dur = datetime.timedelta(days=random.randint(1, 4))
        #     prog = random.randint(1, 100)
        #     pred = random.choice(tasks)
        #     # pred = list(project.tasks.all())[-1]
        #     selected = ProjectTask.objects.get_or_create(
        #         project=project,
        #         name='caulk tile'
        #         )[0]
        #     selected.parent = parent_task
        #     selected.predecessor = pred
        #     selected.start_date = None
        #     selected.duration = dur
        #     selected.progress = prog
        #     selected.save()

            
        # qs = SearchIndex.objects.filter(name='Hoffman, Morales and Peters demo 2')
        # for q in qs:
        #     print(q)
        # create_indexes()
        # alla = Appliance.objects.all()
        # for a in alla:
        #     a.add_proprietary_files()
        # ConfigTree.refresh()
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



