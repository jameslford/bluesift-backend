import decimal 
from typing import Dict
from django.db import models, transaction
from django.core.exceptions import ValidationError
from model_utils import Choices
from model_utils.managers import InheritanceManager
from Addresses.models import Address
from Retailers.models import RetailerLocation, RetailerProduct
from Profiles.models import ConsumerProfile, ProEmployeeProfile
from Products.models import Product
from Groups.models import ProCompany
from Groups.serializers import BusinessSerializer
from Profiles.serializers import serialize_profile
# from UserProductCollections.models import BaseProject, RetailerLocation
# from UserProducts.models import RetailerProduct

DAY = 60*60*24*1000

class BaseProjectManager(models.Manager):
    """
    manager for projects, cosumer and pro. only adds 1 custom method: create_project
    """
    @transaction.atomic()
    def create_project(self, user, **kwargs):
        """
        can pass any verified user to this method and will create the correct project_type, or return none
        if user.is_supplier
        """
        nickname = kwargs.get('nickname')
        deadline = kwargs.get('deadline')
        address = kwargs.get('address_pk')
        project = None
        group = user.get_group()
        if user.is_pro:
            project = ProProject.objects.create(owner=group, nickname=nickname, deadline=deadline)
        else:
            project = ConsumerProject.objects.create(owner=group, nickname=nickname, deadline=deadline)
        if not address:
            return project
        address = Address.objects.filter(pk=address).first()
        if not address:
            return project
        project.address = address
        project.save()
        return project

    def update_project(self, user, **kwargs):
        """ update method """
        project_pk = kwargs.get('pk')
        if isinstance(project_pk, list):
            project_pk = project_pk[0]
        if isinstance(project_pk, str):
            project_pk = int(project_pk)
        project_pk = int(project_pk)
        collections = user.get_collections()
        collection = collections.get(pk=project_pk)
        nickname = kwargs.get('nickname')
        deadline = kwargs.get('deadline')
        address = kwargs.get('address')
        image = kwargs.get('image')
        if deadline:
            collection.deadline = deadline
        if address:
            address = Address.objects.get(pk=address)
            collection.address = address
        if nickname:
            collection.nickname = nickname
        if image:
            try:
                image = image[0]
                collection.image.save(image.name, image)
                print('image saved')
            except IndexError:
                pass
        collection.save()
        return collection

    def get_user_projects(self, user, project_pk=None):
        """
        returns correct subclass of BaseProject based on user
        if project_pk is provided, returns a project instance, else returns a queryset
        """
        if user.is_admin or user.is_supplier:
            raise ValueError('Unsupported user type')
        if user.is_pro:
            group = user.get_group()
            projects = ProProject.objects.filter(owner=group)
            if project_pk:
                return projects.get(pk=project_pk)
            return projects
        projects = ConsumerProject.objects.filter(owner__user=user)
        if project_pk:
            return projects.get(pk=project_pk)
        return projects


class BaseProject(models.Model):
    deadline = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='project-images/' )
    template = models.BooleanField(default=False)
    address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='projects'
    )

    objects = BaseProjectManager()
    subclasses = InheritanceManager()

    def product_count(self):
        return self.products.count()

    def application_count(self):
        # pylint: disable=no-member
        if self.applications:
            return self.applications.count()
        return 0


class ProProject(BaseProject):
    nickname = models.CharField(max_length=60)
    owner = models.ForeignKey(
        ProCompany,
        on_delete=models.CASCADE,
        related_name='projects'
    )

    class Meta:
        unique_together = ('nickname', 'owner')

    def save(self, *args, **kwargs):
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = 'Project ' + str(count)
        self.full_clean()
        return super().save(*args, **kwargs)


class ConsumerProject(BaseProject):
    nickname = models.CharField(max_length=60)
    owner = models.ForeignKey(
        ConsumerProfile,
        on_delete=models.CASCADE,
        related_name='projects'
        )

    class Meta:
        unique_together = ('nickname', 'owner')

    def __str__(self):
        return self.nickname

    def clean(self):
        # pylint: disable=no-member
        projects_allowed = self.owner.plan.project_theshhold if self.owner.plan else 10
        existing_projects = self.owner.projects.all().count()
        if existing_projects <= projects_allowed:
            return super().clean()
        raise ValidationError("Already at plan's project quota")

    def save(self, *args, **kwargs):
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = 'Project ' + str(count)
        self.full_clean()
        return super().save(*args, **kwargs)

class ProjectProductManager(models.Manager):
    def add_product(self, user, product_pk, collection_pk=None):
        collections = user.get_collections()
        collection = collections.filter(
            pk=collection_pk).first() if collection_pk else collections.first()
        product = Product.objects.get(pk=product_pk)
        self.get_or_create(product=product, project=collection)[0]
        return True

    def delete_product(self, user, product_pk, collection_pk=None):
        collections = user.get_collections()
        collection = collections.filter(
            pk=collection_pk).first() if collection_pk else collections.first()
        user_product = self.get(product__pk=product_pk, project=collection)
        user_product.delete()
        return True


class ProjectProduct(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        related_name='customer_products'
        )
    project = models.ForeignKey(
        BaseProject,
        on_delete=models.CASCADE,
        related_name='products'
        )

    objects = ProjectProductManager()

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ('product', 'project')


class ProductAssignmentManager(models.Manager):

    @transaction.atomic()
    def update_assignments(self, project, *args):
        for arg in args:
            pk = arg.get('pk')
            assignment: ProductAssignment = self.model.objects.get(pk=pk) if pk else self.model()

            assignment.project = project
            assignment.name = arg.get('name')
            assignment.quantity_needed = arg.get('quantity', 0)
            assignment.procured = arg.get('procured', False)

            supplier = arg.get('supplier')
            product = arg.get('product')
            if product:
                product_pk = product.get('pk')
                product = Product.objects.get(pk=product_pk)
                assignment.product = product

                if supplier:
                    location_pk = supplier.get('location_pk')
                    assignment.supplier = RetailerLocation.objects.get(pk=location_pk)
            assignment.save()


class ProductAssignment(models.Model):
    name = models.CharField(max_length=80)
    quantity_needed = models.IntegerField()
    procured = models.BooleanField(default=False)
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
    supplier_product = models.ForeignKey(
        RetailerProduct,
        on_delete=models.CASCADE,
        related_name='project_assignments',
        null=True
    )

    objects = ProductAssignmentManager()

    class Meta:
        unique_together = ('project', 'name')

    def save(self, *args, **kwargs):
        if self.supplier and not self.supplier_product:
            prod = RetailerProduct.objects.filter(retailer=self.supplier, product=self.product).first()
            self.supplier_product = prod if prod else None
        if self.supplier_product and not self.supplier:
            self.supplier = self.supplier_product.retailer
        super(ProductAssignment, self).save(*args, **kwargs)

    def mini_serialize(self):
        cost = None
        if self.supplier_product and self.quantity_needed:
            cost = self.supplier_product.in_store_ppu * decimal.Decimal(self.quantity_needed)
        return {
            'name': self.name,
            'cost': cost if cost else 0
            }

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
    level = models.IntegerField(default=0)
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
        on_delete=models.CASCADE,
        related_name='tasks'
        )
    product = models.ForeignKey(
        ProductAssignment,
        null=True,
        on_delete=models.SET_NULL,
        related_name='task'
        )

    def save(self, *args, **kwargs):
        self.count_parents()
        super(ProjectTask, self).save(*args, **kwargs)

    def count_parents(self):
        level = 0
        if self.parent:
            level = 1
            if self.parent.parent:
                level = 2
                if self.parent.parent.parent:
                    raise ValueError('Only 2 nested levels allowed')
        self.level = level

    def mini_serialize(self) -> Dict[str, any]:
        return {
            'pk': self.pk,
            'name': self.name,
            # 'assigned_product': serializer_product_assignment(self.product) if self.product else None,
            'progress': self.progress,
            'saved': True,
            'start_date': self.start_date,
            'duration': self.duration / DAY if self.duration else None,
            'children': [child.mini_serialize() for child in self.children.all()],
            # 'predecessor': serialize_self(self.predecessor) if self.predecessor else None
            }

class AddtionalProjectCosts(models.Model):
    project = models.ForeignKey(
        BaseProject,
        on_delete=models.CASCADE,
        related_name='additional_costs'
        )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    label = models.CharField(max_length=60)
    notes = models.TextField(null=True, blank=True)


class Bid(models.Model):
    task = models.ForeignKey(
        ProjectTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='bids'
        )
    project = models.ForeignKey(
        BaseProject,
        on_delete=models.CASCADE,
        related_name='bids'
        )
    company = models.ForeignKey(
        ProCompany,
        on_delete=models.CASCADE,
        related_query_name='bids'
        )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    accepted = models.BooleanField(default=False)
    files = models.FileField(null=True, upload_to='bids/')
    role = models.CharField(max_length=100, blank=True, null=True)
    message = models.TextField(null=True, blank=True)
    assigned_to = models.ForeignKey(
        ProEmployeeProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
        )

    def save(self, *args, **kwargs):
        if self.assigned_to and self.assigned_to.company != self.company:
            raise ValidationError('Can only assign to company employee')
        if not self.project:
            if not self.task:
                raise ValidationError('No project or task to assign')
            self.project = self.task.project
        super(Bid, self).save(*args, **kwargs)


class BidInvitation(models.Model):
    message = models.TextField(null=True, blank=True)
    task = models.ForeignKey(
        ProjectTask,
        on_delete=models.CASCADE,
        related_name='bid_invites',
        null=True,
        blank=True
        )
    company = models.ForeignKey(
        ProCompany,
        on_delete=models.CASCADE,
        related_query_name='bid_invites'
        )
    project = models.ForeignKey(
        BaseProject,
        on_delete=models.CASCADE,
        related_name='bid_invites',
        null=True,
        blank=True
        )

    def save(self, *args, **kwargs):
        if not self.project:
            if not self.task:
                raise ValidationError('No project or task to assign')
            self.project = self.task.project
        super(BidInvitation, self).save(*args, **kwargs)



# class ProCollaborator(Collaborator):
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

# class ConsumerCollaborator(Collaborator):
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
