import datetime
from decimal import Decimal
from django.db import models
from django.core.exceptions import ValidationError
# from django.db.models import Avg
from django.conf import settings
from Addresses.models import Address
from Products.models import Product
from Plans.models import SupplierPlan


class CompanyAccount(models.Model):
    name = models.CharField(max_length=40, unique=True)
    headquarters = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=12, null=True, blank=True)
    plan = models.ForeignKey(SupplierPlan, null=True, on_delete=models.SET_NULL, related_name='suppliers')
    email_verified = models.BooleanField(default=False)
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return self.name

    def get_employees(self):
        # pylint: disable=no-member
        return self.employees

    def shipping_location_count(self):
        try:
            count = self.shipping_locations.count()
            return count
        except:
            return 0


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

    def __str__(self):
        return self.user.email

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
                raise ValidationError('Maximum owners, ' + str(company_owners_allowed) + ' already exist')
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
    info = models.CharField(max_length=200, blank=True, null=True)
    website = models.URLField(max_length=300, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='storefronts/')
    slug = models.SlugField(null=True, blank=True)

    def __str__(self):
        return str(self.company_account) + ' ' + str(self.number)

    def average_rating(self):
        avg_rating = self.ratings.all().aggregate(models.Avg('rating'))
        avg_rating = avg_rating.get('rating_avg', None)
        return avg_rating

    def rating_count(self):
        return self.ratings.all().count()

    def location_manager(self):
        if self.local_admin:
            return [self.local_admin.id, self.local_admin.user.get_first_name()]
        sys_admin = self.company_account.employees.filter(company_account_admin=True).first()
        if sys_admin:
            return [sys_admin.id, sys_admin.user.get_first_name()]
        owner = self.company_account.employees.filter(company_account_owner=True).first()
        return [owner.id, owner.user.get_first_name()]

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
        null=True,
        on_delete=models.SET_NULL,
        related_name='priced'
        )

    supplier = models.ForeignKey(
        CompanyShippingLocation,
        on_delete=models.CASCADE,
        related_name='priced_products'
        )

    units_available_in_store = models.IntegerField(default=0, null=True)
    units_per_order = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    for_sale_in_store = models.BooleanField(default=False)
    in_store_ppu = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    product_bb_sku = models.CharField(max_length=60, unique=True)

    for_sale_online = models.BooleanField(default=False)
    online_ppu = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    lead_time_ts = models.DurationField(blank=True, null=True, default=datetime.timedelta(days=0))
    offer_installation = models.BooleanField(default=False)
    banner_item = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'supplier')

    def __str__(self):
        return str(self.supplier) + ' ' + str(self.product.name)

    def location_address(self):
        return self.supplier.address.city_state()

    def location_id(self):
        return self.supplier.id

    def percentage_off(self):
        if not self.on_sale and self.sale_price and self.in_store_ppu:
            return None
        return self.sale_price / self.in_store_ppu

    def reset_product(self):
        product = Product.objects.filter(pk=self.product_bb_sku).first()
        if not product:
            self.delete()
        self.product = product
        self.save()

    def set_banner(self):
        if not self.banner_item:
            return
        location_banner_item_count = self.supplier.priced_products.filter(banner_item=True).count()
        if location_banner_item_count >= 3:
            self.banner_item = False
            return

    def company_name(self):
        return self.supplier.company_account.name

    def coordinates(self):
        coordinates = self.supplier.address.coordinates
        return [coordinates.lat, coordinates.lng]

    def set_online_price(self):
        if self.in_store_ppu:
            self.online_ppu = Decimal(self.in_store_ppu) * Decimal(settings.MARKUP)

    def set_self_bb_sku(self):
        bb_sku = self.product.bb_sku
        self.product_bb_sku = bb_sku

    def check_on_sale(self):
        if not self.sale_price or self.sale_price <= 0:
            self.on_sale = False

    def check_availability(self):
        if self.units_available_in_store <= 0:
            self.for_sale_in_store = False
            self.for_sale_online = False

    def check_approvals(self):
        if not self.supplier.approved_online_seller:
            self.for_sale_online = False
        if not self.supplier.approved_in_store_seller:
            self.for_sale_in_store = False
