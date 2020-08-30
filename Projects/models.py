import random
from typing import Dict, List
from datetime import timedelta, datetime
import pytz
from django.db import models, transaction, IntegrityError
from django.utils import timezone
from django.core.exceptions import ValidationError
from model_utils import Choices
from model_utils.managers import InheritanceManager
from Addresses.models import Address
from Suppliers.models import SupplierProduct
from .demo_list import PROJECT_MIDDLES, PROJECT_SUFFIXES, ROOMS, SUB_TASKS

DAY = 60 * 60 * 24 * 1000


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
        nickname = kwargs.get("nickname")
        deadline = kwargs.get("deadline")
        address = kwargs.get("address_pk")
        project = None
        group = user.get_group()
        project = Project.objects.create(
            owner=group, nickname=nickname, deadline=deadline
        )
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
        project_pk = kwargs.get("pk")
        if isinstance(project_pk, list):
            project_pk = project_pk[0]
        if isinstance(project_pk, str):
            project_pk = int(project_pk)
        project_pk = int(project_pk)
        collections = user.get_collections()
        collection = collections.get(pk=project_pk)
        nickname = kwargs.get("nickname")
        deadline = kwargs.get("deadline")
        address = kwargs.get("address")
        image = kwargs.get("image")
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
                print("image saved")
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
            raise ValueError("Unsupported user type")
        group = user.get_group()
        projects = Project.objects.filter(owner=group)
        if project_pk:
            return projects.get(pk=project_pk)
        return projects


class Project(models.Model):
    deadline = models.DateTimeField(null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True, upload_to="project-images/")
    template = models.BooleanField(default=False)
    # buffer = models.IntegerField(default=10)
    address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="projects",
    )
    nickname = models.CharField(max_length=60)
    owner = models.ForeignKey(
        "Profiles.ConsumerProfile", on_delete=models.CASCADE, related_name="projects"
    )

    objects = ProjectManager()
    subclasses = InheritanceManager()

    class Meta:
        unique_together = ("nickname", "owner")

    def __str__(self):
        return self.nickname

    def clean(self):
        # pylint: disable=no-member
        projects_allowed = self.owner.plan.project_theshhold if self.owner.plan else 10
        existing_projects = self.owner.projects.all().count()
        if existing_projects <= projects_allowed:
            return super().clean()
        raise ValidationError("Already at plan's project quota")

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = "Project " + str(count)
        return super().save(*args, **kwargs)

    # def calculate_progress(self):
    #     tasks = self.tasks.all()

    @classmethod
    def create_demo_project(cls, user, address: Address):
        from scripts.demo_data import random_deadline

        deadline = random_deadline()
        middle = random.choice(PROJECT_MIDDLES)
        suffix = random.choice(PROJECT_SUFFIXES)
        nickname = (
            f"{address.get_short_name()} {middle} {suffix}"
            if address
            else f"{middle} {suffix}"
        )
        try:
            project = Project.objects.create_project(
                user=user, nickname=nickname, deadline=deadline
            )
            if address:
                project.address = address
                project.save()
            return project
        except IntegrityError:
            return None

    def create_fake_parent_tasks(self):
        # pylint-disable: nu-member
        if not self.owner.user.demo:
            return

        rooms = ROOMS.copy()
        total_rooms = len(rooms) - 4
        products = [prod.product for prod in self.owner.products.all()]
        task_count = range(random.randint(3, total_rooms))
        for _ in task_count:
            add_assignment = random.choice([True, False])
            task_name = random.choice(rooms)
            task_name = rooms.pop(rooms.index(task_name))
            task = ProjectTask(project=self)
            task.name = task_name
            if add_assignment:
                prod = random.choice(products)
                index = products.index(prod)
                task.product = products.pop(index)
                task.quantity_needed = random.randint(30, 300)
                task.procured = random.choice([True, False])
            task.save()
        project_tasks = list(self.tasks.all())
        while len(project_tasks) > 2:
            rec_task = project_tasks.pop(0)
            pred_task = project_tasks.pop(1)
            rec_task.predecessor = pred_task
            rec_task.save()

    def create_fake_children_task(self):
        # pylint-disable: nu-member
        if not self.owner.user.demo:
            return

        tasks: List[ProjectTask] = ProjectTask.objects.filter(level=0, project=self)
        for task in tasks:
            print("creating children for ", task.name)
            sub_tasks = SUB_TASKS.copy()
            current_child = None
            for child in sub_tasks:
                cont = random.randint(0, 10)
                if cont < 4:
                    continue
                duration = random.randint(3, 5)
                child_task = ProjectTask()
                child_task.parent = task
                child_task.name = child
                child_task.project = task.project
                child_task.duration = datetime.timedelta(days=duration)
                if current_child and random.randint(0, 10) > 4:
                    child_task.predecessor = current_child
                try:
                    child_task.save()
                    current_child = child_task
                except ValidationError:
                    continue


class ProjectTask(models.Model):
    DEPENDENCIES = Choices(
        ("FTS", "Finish to Start"),
        ("STS", "Start to Start"),
        ("FTF", "Finish to Finish"),
    )
    name = models.CharField(max_length=80)
    notes = models.TextField(null=True, blank=True)
    start_date = models.DateTimeField(null=True)
    duration = models.DurationField(null=True)
    predecessor_type = models.CharField(
        choices=DEPENDENCIES, default=DEPENDENCIES.FTS, max_length=20
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    progress = models.IntegerField(default=0)
    level = models.IntegerField(default=0)
    dependency_level = models.PositiveIntegerField(default=0)

    estimated_start = models.DateTimeField(null=True)
    estimated_finish = models.DateTimeField(null=True)

    predecessor = models.ForeignKey(
        "self", null=True, on_delete=models.SET_NULL, related_name="dependants"
    )
    parent = models.ForeignKey(
        "self", null=True, on_delete=models.SET_NULL, related_name="children"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")

    def __str__(self):
        return f"{self.project.nickname}, {self.name}"

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.count_parents()
        if self.progress > 0:
            if not self.start_date or self.start_date > timezone.now():
                self.start_date = timezone.now()
        if self.predecessor is not None and self.predecessor == self.parent:
            raise ValidationError("parent cannot be predecessor")
        self.estimated_start = self.get_estimated_start()
        self.estimated_finish = self.get_estimated_finish()
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

    def get_dependency_level(self, level=0):
        nlevel = level
        if self.predecessor:
            nlevel += 1
            return self.predecessor.get_dependency_level(nlevel)
        return nlevel

    def get_lead_time(self):
        prods = self.products.select_related(
            "supplier_product", "product__product"
        ).all()
        if not prods or len(prods) < 1:
            return 0
        times = []
        for prod in prods:
            if prod.procured:
                continue
            if prod.supplier_product:
                times.append(prod.supplier_product.lead_time_ts.total_seconds())
                continue
            priced = prod.product.product.priced.all()
            if not priced:
                return 0
            avg = [price.lead_time_ts.total_seconds() for price in priced]
            avg = sum(avg) / len(avg)
            times.append(avg)
        print(times)
        if len(times) < 1:
            return 0
        return max(times)

    def get_duration(self):
        children = self.children.all()
        if children:
            earliest = None
            latest = None
            for child in children:
                start = child.get_estimated_start()
                finish = child.get_estimated_finish()
                if not earliest or start < earliest:
                    earliest = start
                if not latest or finish > latest:
                    latest = finish
            td = latest - earliest
            return td.total_seconds()
        return self.duration.total_seconds() if self.duration else 0

    def predecessor_type_map(self):
        pred_map = {
            "FTS": self.predecessor.get_estimated_finish(),
            "STS": self.predecessor.get_estimated_start(),
        }
        return pred_map.get(self.predecessor_type)

    def get_estimated_start(self):
        if self.predecessor:
            return self.predecessor_type_map()
        if self.parent:
            return self.parent.get_estimated_start()
        if self.progress > 0:
            if not self.start_date or self.start_date > datetime.now(pytz.utc):
                lead_time = self.get_lead_time()
                return datetime.now(pytz.utc) + timedelta(seconds=lead_time)
            return self.start_date
        if not self.start_date:
            lead_time = self.get_lead_time()
            print(lead_time)
            return datetime.now(pytz.utc) + timedelta(seconds=lead_time)
        return self.start_date

    def get_estimated_finish(self):
        progress = self.progress if self.progress else 0
        duration = self.get_duration()
        dur = (1 - (progress / 100)) * duration
        return self.get_estimated_start() + timedelta(seconds=dur)

    def count_parents(self):
        level = 0
        if self.parent:
            level = 1
            if self.parent.parent:
                level = 2
                if self.parent.parent.parent:
                    raise ValueError("Only 2 nested levels allowed")
        self.level = level

    def mini_serialize(self) -> Dict[str, any]:
        return {
            "pk": self.pk,
            "name": self.name,
            "progress": self.progress,
            "saved": True,
            "start_date": self.start_date,
            "duration": self.duration / DAY if self.duration else None,
            "children": [child.mini_serialize() for child in self.children.all()],
        }


class ProjectProduct(models.Model):
    quantity_needed = models.IntegerField(null=True, blank=True)
    procured = models.BooleanField(default=False)
    project = models.ForeignKey(
        Project, null=True, on_delete=models.CASCADE, related_name="products"
    )
    product = models.ForeignKey(
        "Profiles.LibraryProduct",
        null=True,
        on_delete=models.PROTECT,
        related_name="projects",
    )
    supplier_product = models.ForeignKey(
        SupplierProduct, null=True, on_delete=models.CASCADE, related_name="projects"
    )
    linked_tasks = models.ForeignKey(
        ProjectTask,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="products",
    )

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        if self.supplier_product:
            if self.supplier_product.product != self.product.product:
                raise ValidationError(f"retailer product does not match product")
        if not self.project:
            self.project = self.linked_tasks.project
        if self.product.owner != self.project.owner:
            raise ValidationError("product not in user library")
        return super().save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )


class AddtionalProjectCosts(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="additional_costs"
    )
    amount = models.DecimalField(max_digits=7, decimal_places=2)
    label = models.CharField(max_length=60)
    notes = models.TextField(null=True, blank=True)
