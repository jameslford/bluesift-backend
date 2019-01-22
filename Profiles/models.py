from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from Addresses.models import Address
from Products.models import Product
from Plans.models import SupplierPlan


class CompanyAccount(models.Model):
    name = models.CharField(max_length=120, unique=True)
    headquarters = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    plan = models.ForeignKey(SupplierPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')
    email_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def get_employees(self):
        return self.employees


class EmployeeProfile(models.Model):
    # each user can only have one employee profile
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'is_supplier': True},
        related_name='employee_profile'
    )
    company_account = models.ForeignKey(
        CompanyAccount,
        on_delete=models.CASCADE,
        related_name='employees'
        )
    company_account_owner = models.BooleanField(default=False)
    company_account_admin = models.BooleanField(default=False)
    title = models.CharField(max_length=100, null=True)

    def clean(self):
        # makes sure company owners/admins do not exceed quota
        # hardcoding quota for now, but leaves door open
        company_owners_allowed = 1
        company_admins_allowed = 1
        if self.company_account_admin:
            existing_admins = self.company_account.employees.filter(company_account_admin=True).count()
            if existing_admins >= company_admins_allowed:
                raise ValidationError('Maximum admins, ' + str(company_admins_allowed) + ' already exist')
        if self.company_account_owner:
            existing_owners = self.company_account.employees.filter(company_account_owner=True).count()
            if existing_owners >= company_owners_allowed:
                raise ValidationError('Maximum owners, ' + str(company_owners_allowed) +' already exist')
        return super().clean()

    def save(self, *args, **kwargs):
        # calling full_clean() which executes clean() above
        # among 2 other default methods
        self.full_clean()
        super(EmployeeProfile, self).save(*args, **kwargs)

    def name(self):
        return self.user.get_first_name()

    def email(self):
        return self.user.email


class CompanyShippingLocation(models.Model):
    company_account = models.ForeignKey(
        CompanyAccount,
        on_delete=models.CASCADE,
        related_name='shipping_locations'
        )
    local_admin = models.ForeignKey(
        EmployeeProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        )
    address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=120, null=True, blank=True)
    approved_in_store_seller = models.BooleanField(default=False)
    approved_online_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=10)
    email = models.EmailField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return str(self.company_account) + ' ' + str(self.number)

    def assign_number(self):
        num_list = []
        num = None
        all_locations = self.company_account.shipping_locations.all()
        for loc in all_locations:
            if loc.number:
                num_list.append(loc.number)
            else:
                num_list.append(0)
        if num_list:
            num = max(set(num_list)) + 1
        else:
            num = 1
        return num

    def product_count(self):
        return self.priced_products.count()

    def address_string(self):
        if self.address:
            return self.address.address_string()
        return 'No Address'

    def company_name(self):
        return self.company_account.name

    def clean(self):
        # makes sure employee assigned to local_admin is a company employee
        if not self.local_admin:
            return super().clean()
        if self.local_admin.company_account == self.company_account:
            return super().clean()
        else:
            raise ValidationError('Employee not a company employee')

    def save(self, *args, **kwargs):
        if not self.address:
            self.approved_online_seller = False
        if not self.number:
            self.number = self.assign_number()
        if not self.nickname:
            self.nickname = self.company_account.name + ' ' + str(self.number)
        self.full_clean()
        super(CompanyShippingLocation, self).save(*args, **kwargs)


class SupplierProduct(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='priced'
        )
    supplier = models.ForeignKey(
        CompanyShippingLocation,
        on_delete=models.CASCADE,
        related_name='priced_products'
        )
    my_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    online_ppu = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    units_available = models.IntegerField(default=0, null=True)
    units_per_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    for_sale_in_store = models.BooleanField(default=False)
    for_sale_online = models.BooleanField(default=False)
    offer_installation = models.BooleanField(default=False)

    def __str__(self):
        return str(self.supplier) + ' ' + str(self.product.name)

    def set_online_price(self):
        if self.my_price:
            self.online_ppu = Decimal(self.my_price) * Decimal(settings.MARKUP)

    def save(self, *args, **kwargs):
        self.set_online_price()
        if self.units_available <= 0:
            self.for_sale_in_store = False
            self.for_sale_online = False
        if not self.supplier.approved_online_seller:
            self.for_sale_online = False
        if not self.supplier.approved_in_store_seller:
            self.for_sale_in_store = False
        super(SupplierProduct, self).save(*args, **kwargs)  # Call the real save() method
        self.product.set_prices()
        if self.supplier.address:
            self.product.set_locations()

    class Meta:
        unique_together = ('product', 'supplier')

    def delete(self, using=None, keep_parents=False):
        address = False
        if self.supplier.address:
            address = True
        product = self.product
        super().delete(using=using, keep_parents=keep_parents)
        product.set_prices()
        if address:
            product.set_locations()
