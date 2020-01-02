# import decimal 
# from typing import Dict
# from django.db import models, transaction
# from model_utils import Choices
# from UserProductCollections.models import BaseProject, RetailerLocation
# from Profiles.models import ConsumerProfile, ProEmployeeProfile
# from Products.models import Product
# from Groups.models import ProCompany
# from Groups.serializers import BusinessSerializer
# from Profiles.serializers import serialize_profile
# from UserProducts.models import RetailerProduct

# DAY = 60*60*24*1000


# class ProductAssignmentManager(models.Manager):

    # @transaction.atomic()
    # def create_assignment(self, project, *args, **kwargs):
    #     name = kwargs.get('name')
    #     product = kwargs.get('product')
    #     product_pk = product.get('pk')
    #     product = Product.objects.get(pk=product_pk)
    #     quantity = kwargs.get('quantity_needed', 0)
    #     supplier = kwargs.get('supplier')
    #     assignment = self.model.objects.get_or_create(
    #         name=name,
    #         product=product,
    #         project=project,
    #         quantity_needed=quantity
    #         )[0]
    #     if supplier and supplier != 'auto':
    #         supplier_pk = supplier.get('location_pk')
    #         retailer_product = RetailerLocation.objects.filter(pk=supplier_pk).first()
    #         assignment.supplier = retailer_product
    #         assignment.save()
    #     return assignment

#     @transaction.atomic()
#     def update_assignments(self, project, *args):
#         for arg in args:
#             pk = arg.get('pk')
#             assignment: ProductAssignment = self.model.objects.get(pk=pk) if pk else self.model()

#             assignment.project = project
#             assignment.name = arg.get('name')
#             assignment.quantity_needed = arg.get('quantity', 0)
#             assignment.procured = arg.get('procured', False)

#             supplier = arg.get('supplier')
#             product = arg.get('product')
#             if product:
#                 product_pk = product.get('pk')
#                 product = Product.objects.get(pk=product_pk)
#                 assignment.product = product

#                 if supplier:
#                     location_pk = supplier.get('location_pk')
#                     assignment.supplier = RetailerLocation.objects.get(pk=location_pk)
#             assignment.save()


# class ProductAssignment(models.Model):
#     name = models.CharField(max_length=80)
#     quantity_needed = models.IntegerField()
#     procured = models.BooleanField(default=False)
#     project = models.ForeignKey(
#         BaseProject,
#         on_delete=models.CASCADE,
#         related_name='product_assignments'
#         )
#     product = models.ForeignKey(
#         Product,
#         on_delete=models.CASCADE,
#         related_name='project_assignments'
#         )
#     supplier = models.ForeignKey(
#         RetailerLocation,
#         on_delete=models.CASCADE,
#         related_name='project_assignments',
#         null=True
#         )
#     supplier_product = models.ForeignKey(
#         RetailerProduct,
#         on_delete=models.CASCADE,
#         related_name='project_assignments',
#         null=True
#     )

#     objects = ProductAssignmentManager()

#     class Meta:
#         unique_together = ('project', 'name')

#     def save(self, *args, **kwargs):
#         if self.supplier and not self.supplier_product:
#             prod = RetailerProduct.objects.filter(retailer=self.supplier, product=self.product).first()
#             self.supplier_product = prod if prod else None
#         if self.supplier_product and not self.supplier:
#             self.supplier = self.supplier_product.retailer
#         super(ProductAssignment, self).save(*args, **kwargs)

#     def mini_serialize(self):
#         cost = None
#         if self.supplier_product and self.quantity_needed:
#             cost = self.supplier_product.in_store_ppu * decimal.Decimal(self.quantity_needed)
#         return {
#             'name': self.name,
#             'cost': cost
#             }


# class ProCollaborator(models.Model):
#     project = models.ForeignKey(
#         BaseProject,
#         on_delete=models.CASCADE,
#         related_name='pro_collaborators'
#         )
#     role = models.CharField(max_length=80, null=True)
#     collaborator = models.ForeignKey(
#         ProCompany,
#         on_delete=models.CASCADE,
#         related_name='collaborations'
#         )
#     contact = models.ForeignKey(
#         ProEmployeeProfile,
#         null=True,
#         on_delete=models.SET_NULL,
#         related_name='collaborations'
#         )

#     class Meta:
#         unique_together = ('project', 'collaborator')

#     def __str__(self):
#         return str(self.project.pk) + ' ' + str(self.collaborator.pk)

#     def save(self, *args, **kwargs):
#         if self.contact and self.contact.company != self.collaborator:
#             raise ValueError('Contact does not belong to company')
#         super(ProCollaborator, self).save(*args, **kwargs)

#     def serialize(self):
#         return {
#             'business': BusinessSerializer(self.collaborator).getData(),
#             'contact': serialize_profile(profile=self.contact),
#             'role': self.role
#             }


# class ConsumerCollaborator(models.Model):
#     project = models.ForeignKey(
#         BaseProject,
#         on_delete=models.CASCADE,
#         related_name='collaborators'
#         )
#     role = models.CharField(max_length=80, null=True)
#     collaborator = models.ForeignKey(
#         ConsumerProfile,
#         on_delete=models.CASCADE,
#         related_name='collaborations'
#         )


#     def serialize(self):
#         return {
#             'collaborator': serialize_profile(self.collaborator),
#             'role': self.role
#             }

# class ProjectTask(models.Model):
#     DEPENDENCIES = Choices(('FTS', 'Finish to Start'), ('STS', 'Start to Start'), ('FTF', 'Finish to Finish'))
#     name = models.CharField(max_length=80)
#     notes = models.TextField(null=True, blank=True)
#     start_date = models.DateTimeField(null=True)
#     duration = models.DurationField(null=True)
#     predecessor_type = models.CharField(choices=DEPENDENCIES, default=DEPENDENCIES.FTS, max_length=20)
#     created = models.DateTimeField(auto_now_add=True)
#     updated = models.DateTimeField(auto_now=True)
#     progress = models.IntegerField(null=True)
#     level = models.IntegerField(default=0)
#     pro_collaborator = models.ForeignKey(
#         ProCollaborator,
#         null=True,
#         on_delete=models.SET_NULL
#         )
#     user_collaborator = models.ForeignKey(
#         ConsumerCollaborator,
#         null=True,
#         on_delete=models.SET_NULL
#         )
#     predecessor = models.ForeignKey(
#         'self',
#         null=True,
#         on_delete=models.SET_NULL,
#         related_name='dependants'
#         )
#     parent = models.ForeignKey(
#         'self',
#         null=True,
#         on_delete=models.SET_NULL,
#         related_name='children'
#         )
#     project = models.ForeignKey(
#         BaseProject,
#         on_delete=models.CASCADE,
#         related_name='tasks'
#         )
#     product = models.ForeignKey(
#         ProductAssignment,
#         null=True,
#         on_delete=models.SET_NULL,
#         related_name='task'
#         )

#     def save(self, *args, **kwargs):
#         self.count_parents()
#         if self.user_collaborator and self.pro_collaborator:
#             raise ValueError('cannot have 2 collaborators')
#         super(ProjectTask, self).save(*args, **kwargs)

#     def count_parents(self):
#         level = 0
#         if self.parent:
#             level = 1
#             if self.parent.parent:
#                 level = 2
#                 if self.parent.parent.parent:
#                     raise ValueError('Only 2 nested levels allowed')
#         self.level = level

#     def collaborator(self):
#         if self.pro_collaborator:
#             return self.pro_collaborator.pk
#         if self.user_collaborator:
#             return self.user_collaborator.pk
#         return None

#     def mini_serialize(self) -> Dict[str, any]:
#         return {
#             'pk': self.pk,
#             'name': self.name,
#             'assigned_to': self.collaborator(),
#             # 'assigned_product': serializer_product_assignment(self.product) if self.product else None,
#             'progress': self.progress,
#             'saved': True,
#             'start_date': self.start_date,
#             'duration': self.duration / DAY if self.duration else None,
#             'children': [child.mini_serialize() for child in self.children.all()],
#             # 'predecessor': serialize_self(self.predecessor) if self.predecessor else None
#             }
