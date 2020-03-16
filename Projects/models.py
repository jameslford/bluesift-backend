from typing import Dict
from datetime import timedelta, datetime
import pytz
from django.db import models, transaction
# from django.db.models import Min, Max, F, Sum, DateTimeField, DecimalField, ExpressionWrapper, DurationField
from django.core.exceptions import ValidationError
from model_utils import Choices
from model_utils.managers import InheritanceManager
from Addresses.models import Address
from Suppliers.models import SupplierProduct
from Profiles.models import ConsumerProfile, LibraryProduct

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
    start_date = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to='project-images/' )
    template = models.BooleanField(default=False)
    # buffer = models.IntegerField(default=10)
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

    def calculate_progress(self):
        tasks = self.tasks.all()



class ProjectTask(models.Model):
    DEPENDENCIES = Choices(('FTS', 'Finish to Start'), ('STS', 'Start to Start'), ('FTF', 'Finish to Finish'))
    name = models.CharField(max_length=80)
    notes = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)
    estimated_finish = models.DateTimeField(null=True)
    predecessor_type = models.CharField(choices=DEPENDENCIES, default=DEPENDENCIES.FTS, max_length=20)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    progress = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    dependency_level = models.PositiveIntegerField(default=0)
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

    def __str__(self):
        return f'{self.project.nickname}, {self.name}'

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.count_parents()
        self.start_date = self.get_start_date()
        self.estimated_finish = self.get_estimated_finish()
        self.dependency_level = self.get_dependency_level()
        if self.predecessor is not None and self.predecessor == self.parent:
            raise ValidationError('parent cannot be predecessor')
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def get_dependency_level(self, level=0):
        nlevel = level
        if self.predecessor:
            nlevel += 1
            return self.predecessor.get_dependency_level(nlevel)
        return nlevel


    def get_duration(self):
        children = self.children.all()
        if children:
            earliest = None
            latest = None
            for child in children:
                start = child.get_start_date()
                finish = child.get_estimated_finish()
                if not earliest or start < earliest:
                    earliest = start
                if not latest or finish > latest:
                    latest = finish
            td = latest - earliest
            return td.total_seconds()
        return self.duration.total_seconds()


    def get_start_date(self):
        start_date = datetime.now(pytz.utc)
        if self.predecessor:
            if self.predecessor_type == 'FTS':
                start_date = self.predecessor.get_estimated_finish()
            if self.predecessor_type == 'STS':
                start_date = self.predecessor.get_start_date()
        elif self.parent:
            start_date = self.parent.get_start_date()
        else:
            if self.progress > 0:
                if not self.start_date or self.start_date > datetime.now(pytz.utc):
                    start_date = datetime.now(pytz.utc)
                else:
                    start_date = self.start_date
            else:
                if not self.start_date or self.start_date < datetime.now(pytz.utc):
                    return datetime.now(pytz.utc)
                else:
                    start_date = self.start_date
        return start_date


    def get_estimated_finish(self):
        progress = self.progress if self.progress else 0
        duration = self.get_duration()
        dur = (1 - (progress/100)) * duration
        return self.get_start_date() + timedelta(seconds=dur)


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


class ProjectProduct(models.Model):
    quantity_needed = models.IntegerField(null=True, blank=True)
    procured = models.BooleanField(default=False)
    project = models.ForeignKey(
        Project,
        null=True,
        on_delete=models.SET_NULL,
        related_name='products'
        )
    product = models.ForeignKey(
        LibraryProduct,
        null=True,
        on_delete=models.PROTECT,
        related_name='projects'
        )
    supplier_product = models.ForeignKey(
        SupplierProduct,
        null=True,
        on_delete=models.SET_NULL,
        related_name='projects'
        )
    linked_tasks = models.ForeignKey(
        ProjectTask,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products'
        )

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.supplier_product:
            if self.supplier_product.product != self.product.product:
                raise ValidationError(f'retailer product does not match product')
        if self.product.owner != self.project.owner:
            raise ValidationError('product not in user library')
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)


class AddtionalProjectCosts(models.Model):
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='additional_costs'
        )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    label = models.CharField(max_length=60)
    notes = models.TextField(null=True, blank=True)
