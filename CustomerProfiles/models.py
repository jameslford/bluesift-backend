from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from model_utils import Choices
from config.scripts.globals import valid_subclasses
from Addresses.models import Address
from Products.models import Product, ProductSubClass
from Plans.models import CustomerPlan



class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='customer_profile'
        )
    addresses = models.ManyToManyField(Address, related_name='addresses')
    phone_number = models.IntegerField(null=True)
    name = models.CharField(max_length=40, blank=True, null=True)
    plan = models.ForeignKey(CustomerPlan, null=True, on_delete=models.SET_NULL, related_name='customers')

    def __str__(self):
        return self.user.get_first_name() + "'s library"

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.user.get_first_name() + "'s library"
        super(CustomerProfile, self).save(*args, **kwargs)


class CustomerProject(models.Model):
    owner = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='projects'
        )
    address = models.ForeignKey(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='projects'
        )
    nickname = models.CharField(max_length=50, null=True, blank=True)
    deadline = models.DateTimeField(null=True, blank=True)
    template = models.BooleanField(default=False)

    def __str__(self):
        return self.nickname

    def product_count(self):
        return self.products.count()

    def application_count(self):
        # pylint: disable=no-member
        if self.applications:
            return self.applications.count()
        return 0

    def clean(self):
        # pylint: disable=no-member
        projects_allowed = self.owner.plan.project_theshhold if self.owner.plan else 10
        existing_projects = self.owner.projects.all().count()
        if existing_projects <= projects_allowed:
            return super().clean()
        raise ValidationError("Already at plan's project quota")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save()
        if not self.nickname:
            count = self.owner.projects.count() + 1
            self.nickname = 'Project ' + str(count)
        return super().save(*args, **kwargs)


class CustomerProduct(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        related_name='customer_products'
        )
    project = models.ForeignKey(
        CustomerProject,
        on_delete=models.CASCADE,
        related_name='products'
        )

    def __str__(self):
        return self.product.name

    class Meta:
        unique_together = ('product', 'project')


class CustomerProjectApplication(models.Model):
    # choice_tuple = [cls.__name__ for cls in ProductSubClass.__subclasses__()]
    # category_choices = Choices((cls.__name__ for cls in ProductSubClass.__subclasses__()))
    category_choices = valid_subclasses() + ['other']
    label = models.CharField(max_length=100, blank=True, null=True)
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, blank=True, related_name='applications')
    product = models.ForeignKey(CustomerProduct, blank=True, null=True, on_delete=models.SET_NULL)
    quantity = models.IntegerField()
    category = Choices(category_choices)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    # category = models.ForeignKey(
    #     ContentType,
    #     null=True,
    #     blank=True,
    #     on_delete=models.SET_NULL
    #     )

    class Meta:
        unique_together = ('label', 'project')

    def __str__(self):
        return self.label

    def unit(self):
        pass

    def get_product_model(self):
        pass


    def check_product(self):
        # pylint: disable=no-member
        if self.product in self.project.customer_products:
            return
        raise Exception('Product not in customer project')

    # def check_content_type(self):
    #     valid_subs = valid_subclasses() + ['other']
    #     if self.category.

    # def category_selections(self):
    #     from Products.models import ProductSubClass
    #     choices = [cls.__name__ for cls in ProductSubClass.__subclasses__()] + ['other']
    #     return tuple(choices)

