# """
# serializers used for return project and retailer locations list to user library
# """

# # from rest_framework import serializers
# from Addresses.serializers import AddressSerializer
# from Schedule.models import ProjectTask, ProductAssignment
# from .models import BaseProject


# def project_serializer(project: BaseProject):
#     return {
#         'pk' : project.pk,
#         'image' : project.image.url if project.image else None,
#         'nickname' : project.nickname,
#         'deadline' : project.deadline,
#         'address' : AddressSerializer(project.address).data,
#         'product_count' : project.product_count(),
#         # 'tasks': []
#         }

# def project_full_serializer(project: BaseProject):
#     return {
#         'pk' : project.pk,
#         'image' : project.image.url if project.image else None,
#         'nickname' : project.nickname,
#         'deadline' : project.deadline,
#         'address' : AddressSerializer(project.address).data,
#         'product_count' : project.product_count(),
#         # 'tasks': []
#     }

# def project_mini_serializer(project: BaseProject):
#     tasks = ProjectTask.objects.prefetch_related(
#         'children',
#         'children__children'
#         ).select_related(
#             'pro_collaborator',
#             'user_collaborator'
#             ).filter(project=project, level=0)
#     assignments = ProductAssignment.objects.select_related(
#         'product',
#         'supplier',
#         'supplier_product'
#         ).filter(project=project)
#     return {
#         'pk' : project.pk,
#         'image' : project.image.url if project.image else None,
#         'nickname' : project.nickname,
#         'deadline' : project.deadline,
#         'address' : AddressSerializer(project.address).data,
#         'product_count' : project.product_count(),
#         'tasks': [task.mini_serialize() for task in tasks],
#         'assignments': [assi.mini_serialize() for assi in assignments]
#         }
# # def project_mini_serializer(project: BaseProject):
# #     return {
# #         'pk' : project.pk,
# #         'image' : project.image.url if project.image else None,
# #         'nickname' : project.nickname,
# #         'deadline' : project.deadline,
# #         'address' : AddressSerializer(project.address).data,
# #         'product_count' : project.product_count(),
# #         'tasks': [task.mini_serialize() for task in project.tasks.filter(level=0)],
# #         'assignments': [assi.mini_serialize() for assi in project.product_assignments.all()]
# #         }
