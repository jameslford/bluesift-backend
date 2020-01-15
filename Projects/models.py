from typing import Dict
from django.db import models, transaction
from django.core.exceptions import ValidationError
from model_utils import Choices
from model_utils.managers import InheritanceManager
from Addresses.models import Address
from Suppliers.models import SupplierLocation, SupplierProduct
from Products.models import Product
from Profiles.models import ConsumerProfile

DAY = 60*60*24*1000

class ProjectManager(models.Manager):
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
        project = Project.objects.create(owner=group, nickname=nickname, deadline=deadline)
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
        returns correct subclass of Project based on user
        if project_pk is provided, returns a project instance, else returns a queryset
        """
        if user.is_admin or user.is_supplier:
            raise ValueError('Unsupported user type')
        group = user.get_group()
        projects = Project.objects.filter(owner=group)
        if project_pk:
            return projects.get(pk=project_pk)
        return projects


class Project(models.Model):
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
    nickname = models.CharField(max_length=60)
    owner = models.ForeignKey(
        ConsumerProfile,
        on_delete=models.CASCADE,
        related_name='projects'
        )

    objects = ProjectManager()
    subclasses = InheritanceManager()

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
        return super().save(*args, **kwargs)


class LibraryProductManager(models.Manager):

    def add_product(self, user, product_pk):
        if user.is_supplier:
            raise Exception('supplier cannot add libraryproduct')
        product = Product.objects.get(pk=product_pk)
        group = user.get_group()
        LibraryProduct.objects.get_or_create(product=product, owner=group)
        return True

    def delete_product(self, user, product_pk):
        if user.is_supplier:
            raise Exception('supplier cannot delete libraryproduct')
        product = Product.objects.get(pk=product_pk)
        group = user.get_group()
        product = LibraryProduct.objects.get(product=product, owner=group)
        product.delete()
        return True


class LibraryProduct(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        related_name='project_products'
        )
    owner = models.ForeignKey(
        ConsumerProfile,
        on_delete=models.CASCADE,
        related_name='products'
        )

    objects = LibraryProductManager()
    subclasses = InheritanceManager()

    class Meta:
        unique_together = ('product', 'owner')

    def __str__(self):
        return self.product.name


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
    quantity_needed = models.IntegerField(null=True, blank=True)
    procured = models.BooleanField(default=False)
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
        Project,
        on_delete=models.CASCADE,
        related_name='tasks'
        )
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        related_name='task'
        )
    selected_retailer = models.ForeignKey(
        SupplierLocation,
        null=True,
        on_delete=models.SET_NULL,
        related_name='task'
        )
    retailer_product = models.ForeignKey(
        SupplierProduct,
        null=True,
        on_delete=models.SET_NULL,
        related_name='task'
        )

    def save(self, *args, **kwargs):
        if self.product and self.selected_retailer:
            self.retailer_product = SupplierProduct.objects.filter(
                retailer=self.selected_retailer,
                product=self.product).first()
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
            'progress': self.progress,
            'saved': True,
            'start_date': self.start_date,
            'duration': self.duration / DAY if self.duration else None,
            'children': [child.mini_serialize() for child in self.children.all()],
            }

class AddtionalProjectCosts(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='additional_costs'
        )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    label = models.CharField(max_length=60)
    notes = models.TextField(null=True, blank=True)
