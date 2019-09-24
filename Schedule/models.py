from django.db import models, transaction
from model_utils import Choices
from UserProductCollections.models import BaseProject, RetailerLocation
from UserProducts.models import RetailerProduct
from Profiles.models import ConsumerProfile, ProEmployeeProfile
from Products.models import Product
from Groups.models import ProCompany


class ProductAssignmentManager(models.Manager):

    @transaction.atomic()
    def create_assignment(self, project, **kwargs):
        name = kwargs.get('name')
        product = kwargs.get('product')
        product_pk = product.get('pk')
        product = Product.objects.get(pk=product_pk)
        quantity = kwargs.get('quantity_needed', 0)
        supplier = kwargs.get('supplier')
        assignment = self.model.objects.get_or_create(
            name=name,
            product=product,
            project=project,
            quantity_needed=quantity
            )[0]
        if supplier and supplier != 'auto':
            supplier_pk = supplier.get('location_pk')
            retailer_product = RetailerLocation.objects.filter(pk=supplier_pk).first()
            assignment.supplier = retailer_product
            assignment.save()
        return assignment


class ProductAssignment(models.Model):
    name = models.CharField(max_length=80)
    quantity_needed = models.IntegerField()
    project = models.ForeignKey(
        BaseProject,
        on_delete=models.CASCADE,
        related_name='product_assignments'
        )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='project_assignments'
        )
    supplier = models.ForeignKey(
        RetailerLocation,
        on_delete=models.CASCADE,
        related_name='project_assignments',
        null=True
        )

    objects = ProductAssignmentManager()

    class Meta:
        unique_together = ('project', 'name')


class ProCollaborator(models.Model):
    project = models.ForeignKey(
        BaseProject,
        on_delete=models.CASCADE,
        related_name='pro_collaborators'
        )
    role = models.CharField(max_length=80, null=True)
    collaborator = models.ForeignKey(
        ProCompany,
        on_delete=models.CASCADE,
        related_name='collaborations'
        )
    contact = models.ForeignKey(
        ProEmployeeProfile,
        null=True,
        on_delete=models.SET_NULL,
        related_name='collaborations'
        )

    def save(self, *args, **kwargs):
        if self.contact != self.collaborator:
            raise ValueError('Contact does not belong to company')
        super(ProCollaborator, self).save(*args, **kwargs)


class ConsumerCollaborator(models.Model):
    project = models.ForeignKey(
        BaseProject,
        on_delete=models.CASCADE,
        related_name='collaborators'
        )
    role = models.CharField(max_length=80, null=True)
    collaborator = models.ForeignKey(
        ConsumerProfile,
        on_delete=models.CASCADE,
        related_name='collaborations'
        )


class ProjectTask(models.Model):
    DEPENDENCIES = Choices(('FTS', 'Finish to Start'), ('STS', 'Start to Start'), ('FTF', 'Finish to Finish'))
    name = models.CharField(max_length=80)
    notes = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)
    predecessor_type = models.CharField(choices=DEPENDENCIES, default=DEPENDENCIES.FTS, max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    progress = models.IntegerField(null=True)
    pro_collaborator = models.ForeignKey(
        ProCollaborator,
        null=True,
        on_delete=models.SET_NULL
        )
    user_collaborator = models.ForeignKey(
        ConsumerCollaborator,
        null=True,
        on_delete=models.SET_NULL
        )
    predecessor = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='dependants'
        )
    parent = models.ForeignKey(
        'self',
        null=True,
        on_delete=models.SET_NULL,
        related_name='children'
        )
    project = models.ForeignKey(
        BaseProject,
        null=True,
        on_delete=models.SET_NULL,
        related_name='tasks'
        )
    product = models.ForeignKey(
        ProductAssignment,
        null=True,
        on_delete=models.SET_NULL,
        related_name='task'
        )

    def count_parents(self):
        if self.parent:
            if self.parent.parent:
                if self.parent.parent.parent:
                    raise ValueError('Only 2 nested levels allowed')

    def collaborator(self):
        if self.pro_collaborator:
            return self.pro_collaborator.pk
        if self.user_collaborator:
            return self.user_collaborator.pk
        return None

    def save(self, *args, **kwargs):
        self.count_parents()
        if self.user_collaborator and self.pro_collaborator:
            raise ValueError('cannot have 2 collaborators')
        super(ProjectTask, self).save(*args, **kwargs)
