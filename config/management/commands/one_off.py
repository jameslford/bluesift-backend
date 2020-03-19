from typing import List
import datetime
import random
from django.utils import timezone
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
from scripts.demo_data import create_parent_tasks, create_child_tasks, add_task_products
from Projects.models import ProjectTask, Project, ProjectProduct
from SpecializedProducts.models import Appliance


class Command(BaseCommand):

    def handle(self, *args, **options):
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
        tasks = ProjectTask.objects.all()
        for task in tasks:
            task.save()
        # tasks.delete()
        # create_parent_tasks()
        # create_child_tasks()
        # add_task_products()
