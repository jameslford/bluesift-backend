from django.db import models
from django.conf import settings
from model_utils.managers import InheritanceManager
from Groups.models import SupplierCompany
from Plans.models import ConsumerPlan
from Products.models import Product


class ProfileManager(models.Manager):

    def create_profile(self, user, **kwargs):
        group = kwargs.get('group')
        company = kwargs.get('company')
        company_pk = kwargs.get('company_pk')
        owner = kwargs.get('owner', False)
        admin = kwargs.get('admin', False)
        title = kwargs.get('title', None)
        plan = kwargs.get('plan', None)
        phone = kwargs.get('phone_number', None)
        if user.is_supplier:
            if not company:
                company = SupplierCompany.objects.get(pk=company_pk)
            return SupplierEmployeeProfile.objects.get_or_create(
                user=user,
                company=company,
                owner=owner,
                title=title,
                admin=admin)[0]
        return ConsumerProfile.objects.create(
            user=user,
            group=group,
            phone_number=phone
            )

    def update_profile(self, user, **kwargs):

        profile: BaseProfile = user.get_profile()
        profile_pk = kwargs.get('pk')
        if profile_pk and profile_pk != profile.pk:
            return self.employee_update_by_owner(user, **kwargs)

        avatar = kwargs.get('avatar')
        if avatar:
            if avatar == 'clear':
                profile.avatar = None
            else:
                try:
                    image = avatar[0]
                    profile.avatar.save(image.name, image)
                except IndexError:
                    pass
        full_name = kwargs.get('full_name')
        if full_name:
            user.full_name = full_name
            user.save()
        phone_number = kwargs.get('phone_number')
        if phone_number:
            profile.phone_number = phone_number
        profile.save()
        return profile

    def employee_update_by_owner(self, user, **kwargs):
        return None



class BaseProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='profile'
        )
    collaborators = models.ManyToManyField('BaseProfile', blank=True)
    date_create = models.DateTimeField(auto_now_add=True)
    avatar = models.ImageField(null=True, blank=True, upload_to='profiles/')

    objects = ProfileManager()
    subclasses = InheritanceManager()

    def name(self):
        return self.user.get_full_name()


class ConsumerProfile(BaseProfile):
    phone_number = models.CharField(max_length=30, null=True, blank=True)
    owner = models.BooleanField(default=True)
    plan = models.ForeignKey(
        ConsumerPlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.user.get_first_name() + "'s library"

    # pylint: disable=arguments-differ
    def save(self, *args, **kwargs):
        if self.user.is_supplier:
            raise ValueError('user should not be pro or supplier')
        super(ConsumerProfile, self).save(*args, **kwargs)



class SupplierEmployeeProfile(BaseProfile):
    owner = models.BooleanField(default=False)
    admin = models.BooleanField(default=False)
    publish = models.BooleanField(default=True)
    title = models.CharField(max_length=100, null=True)
    contact_for = models.ManyToManyField('Suppliers.SupplierLocation')
    company = models.ForeignKey(
        SupplierCompany,
        on_delete=models.CASCADE,
        related_name='employees'
        )

    def __str__(self):
        return self.user.get_full_name()

    def locations_managed(self):
        return [location.pk for location in self.managed_locations.all()]

    def save(self, *args, **kwargs):
        # if self.baseprofile_ptr and self.contact_for:
        #     for location in self.contact_for.all():
        #         if location.company != self.company:
        #             raise ValueError('invalid location in contact for')
        if not self.user.is_supplier:
            raise ValueError('user is not retailer')
        super(SupplierEmployeeProfile, self).save(*args, **kwargs)



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
