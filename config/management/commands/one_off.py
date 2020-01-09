# from django.core.management.base import BaseCommand
# from Projects.models import ProjectTask
# from django.db import transaction


# class Command(BaseCommand):
#     @transaction.atomic
#     def handle(self, *args, **options):
#         tasks = ProjectTask.objects.filter(quantity_needed__gt=0, product__isnull=False)
#         for task in tasks:
#             supplier = task.product.priced.first()
#             if supplier:
#                 task.selected_retailer = supplier.retailer
#                 task.save()
