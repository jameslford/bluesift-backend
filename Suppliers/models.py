import datetime
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.postgres.fields import JSONField
from model_utils.managers import InheritanceManager

from Addresses.models import Address
from Products.models import Product
from Groups.models import SupplierCompany
from Profiles.models import SupplierEmployeeProfile
from utils.tree import Tree, SupplierLocationTree



class SupplierLocationManager(models.Manager):

    def create_location(self, user, **kwargs):
        company = user.get_group()
        nickname = kwargs.get('nickname')
        phone_number = kwargs.get('phone_number')
        address_pk = kwargs.get('address_pk')
        if not (company or phone_number or address_pk):
            raise ValidationError('Company, Phone Number, and Address Pk needed')
        local_admin = user.get('local_admin')
        if local_admin:
            local_admin = SupplierEmployeeProfile.objects.get(pk=local_admin)
        address = Address.objects.get(pk=address_pk)
        location = SupplierLocation.objects.create(
            nickname=nickname,
            phone_number=phone_number,
            address=address,
            company=company
            )
        return location

    def update_location(self, user, **kwargs):
        pk = kwargs.get('pk')
        if isinstance(pk, list):
            pk = pk[0]
        if isinstance(pk, str):
            pk = int(pk)
        profile = user.get_profile()
        if not (profile.owner or profile.admin):
            raise PermissionError(f'{user.email} does not have permission to edit this object')
        location: SupplierLocation = user.get_collections().get(pk=pk)
        address_pk = kwargs.get('address_pk', location.address.pk)
        address = Address.objects.get(pk=address_pk)
        location_manager = kwargs.get('location_manager')
        phone_number = kwargs.get('phone_number', location.phone_number)
        nickname = kwargs.get('nickname', location.nickname)
        image = kwargs.get('image')
        if image:
            try:
                image = image[0]
                location.image.save(image.name, image)
                print('image saved')
            except IndexError:
                pass
        location.phone_number = phone_number
        location.nickname = nickname
        location.address = address
        if location_manager:
            location.local_admin = location.company.get_employees().get(pk=location_manager)
        location.save()
        return location


class SupplierLocation(models.Model):
    nickname = models.CharField(max_length=60)
    company = models.ForeignKey(
        SupplierCompany,
        on_delete=models.CASCADE,
        related_name='shipping_locations'
        )
    local_admin = models.ForeignKey(
        SupplierEmployeeProfile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_locations'
        )
    address = models.OneToOneField(
        Address,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        )
    approved_in_store_seller = models.BooleanField(default=False)
    approved_online_seller = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=16)
    email = models.EmailField(null=True, blank=True)
    number = models.IntegerField(null=True, blank=True)
    website = models.URLField(max_length=300, blank=True, null=True)
    image = models.ImageField(null=True, blank=True, upload_to='storefronts/')
    slug = models.SlugField(null=True, blank=True)

    objects = SupplierLocationManager()

    class Meta:
        unique_together = ('nickname', 'company')

    def __str__(self):
        return str(self.company) + ' ' + str(self.number)

    def average_rating(self):
        avg_rating = self.ratings.all().aggregate(models.Avg('rating'))
        avg_rating = avg_rating.get('rating_avg', None)
        return avg_rating

    def rating_count(self):
        return self.ratings.all().count()

    def coordinates(self):
        return [self.address.lat, self.address.lng]

    def company_info(self):
        return self.company.info

    def location_manager(self):
        if self.local_admin:
            return self.local_admin
        sys_admin = self.company.employees.filter(company_account_admin=True).first()
        if sys_admin:
            return sys_admin
        owner = self.company.employees.filter(company_account_owner=True).first()
        return owner


    def address_string(self):
        if self.address:
            return self.address.address_string
        return 'No Address'

    def company_name(self):
        return self.company.name

    # def clean(self):
    #     # TODO makes sure employee assigned to local_admin is a company employee


    def assign_number(self):
        # numbers = self.company.shipping_locations.values_list('number', flat=True)
        numbers = list(SupplierLocation.objects.filter(company=self.company).values_list('number', flat=True))
        if not numbers:
            return 1
        return max(numbers) + 1

    def save(self, *args, **kwargs):
        if not self.address:
            self.approved_in_store_seller = False
            self.approved_online_seller = False
        if not self.number:
            self.number = self.assign_number()
        if not self.nickname:
            self.nickname = self.company.name + ' ' + str(self.number)
        if self.local_admin and self.local_admin.company != self.company:
            raise ValidationError('Employee not a company employee')
        super(SupplierLocation, self).save(*args, **kwargs)
        tree = SupplierProductTree.objects.get_or_create(location=self)[0]
        tree.refresh()


class SupplierProductManager(models.Manager):
    def add_product(self, user, product_pk, collection_pk=None):
        collections = user.get_collections()
        location = collections.filter(
            pk=collection_pk).first() if collection_pk else collections.first()
        profile = user.get_profile()
        if not (profile.admin or
                profile.owner or
                location.local_admin == profile):
            return False
        product = Product.objects.get(pk=product_pk)
        self.get_or_create(product=product, retailer=location)
        return True

    def delete_product(self, user, product, collection_pk):
        collections = user.get_collections()
        location = collections.filter(
            pk=collection_pk).first() if collection_pk else collections.first()
        profile = user.get_profile()
        if not (profile.admin or
                profile.owner or
                location.local_admin == profile):
            return False
        user_prod = self.get(product__pk=product, retailer=location)
        user_prod.delete()


class SupplierProduct(models.Model):
    product = models.ForeignKey(
        Product,
        null=True,
        on_delete=models.SET_NULL,
        related_name='priced'
        )
    location = models.ForeignKey(
        SupplierLocation,
        on_delete=models.CASCADE,
        related_name='products'
        )

    units_available_in_store = models.IntegerField(default=0, null=True)
    units_per_order = models.DecimalField(max_digits=10, decimal_places=2, default=1)

    product_bb_sku = models.CharField(max_length=60)

    publish_in_store_availability = models.BooleanField(default=True)
    publish_in_store_price = models.BooleanField(default=False)
    publish_online_price = models.BooleanField(default=False)

    in_store_ppu = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    online_ppu = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    on_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    lead_time_ts = models.DurationField(blank=True, null=True, default=datetime.timedelta(days=0))
    offer_installation = models.BooleanField(default=False)
    banner_item = models.BooleanField(default=False)

    objects = SupplierProductManager()
    subclasses = InheritanceManager()

    class Meta:
        unique_together = ('product', 'location')

    def __str__(self):
        return str(self.location) + ' ' + str(self.product.name)

    def save(self, *args, **kwargs):
        self.check_approvals()
        self.check_availability()
        if self.publish_in_store_availability:
            self.product.set_locations()
            print('location set')
        return super(SupplierProduct, self).save(*args, **kwargs)

    def serialize_mini(self):
        return {
            'pk': self.pk,
            'in_store_ppu': self.in_store_ppu,
            'units_available_in_store': self.units_available_in_store,
            'units_per_order': self.units_per_order,
            'location_address': self.location.address.city_state(),
            'location_id': self.location.pk,
            'company_name': self.location.company.name,
            'lead_time_ts': self.lead_time_ts.days,
            'publish_online_price': self.publish_online_price,
            'publish_in_store_price': self.publish_in_store_price,
            'publish_in_store_availability': self.publish_in_store_availability
        }

    def get_priced(self):
        return {
            'pk': self.pk,
            'location_pk': self.location.pk,
            'name': self.location.nickname,
            'qty_in_store': self.units_available_in_store,
            'lead_time': self.lead_time_ts,
            'price': self.in_store_ppu,
            }

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
        location_banner_item_count = self.location.products.filter(banner_item=True).count()
        if location_banner_item_count >= 3:
            self.banner_item = False
            return

    def coordinates(self):
        coordinates = self.location.address.coordinates
        return [coordinates.lat, coordinates.lng]

    def check_on_sale(self):
        if not self.sale_price or self.sale_price <= 0:
            self.on_sale = False

    def check_availability(self):
        if self.units_available_in_store <= 0:
            self.publish_in_store_price = False

    def check_approvals(self):
        if not self.location.approved_online_seller:
            self.publish_online_price = False
        if not self.location.approved_in_store_seller:
            self.publish_in_store_price = False
            self.publish_in_store_availability = False



class SupplierProductTree(models.Model):
    tree = JSONField(null=True)
    location = models.OneToOneField(
        SupplierLocation,
        on_delete=models.CASCADE,
        related_name='product_tree'
        )
    product_pks = None

    def get_location_pks(self):
        if self.product_pks:
            return self.product_pks
        self.product_pks = self.location.products.values('product__pk')
        return self.product_pks

    def get_trees(self):
        return SupplierLocationTree(**self.tree)

    def __looper(self, current, parent):
        if not current._meta.abstract:
            pks = self.get_location_pks()
            count = current.objects.filter(pk__in=pks).count()
            if count > 0:
                name = current._meta.verbose_name_plural.lower().strip()
                link = parent.link + '/' + name
                new_tree = SupplierLocationTree(name, count, link)
                parent.children.append(new_tree)
                for sub in current.__subclasses__():
                    self.__looper(sub, new_tree)
        else:
            for child in current.__subclasses__():
                self.__looper(child, parent)

    def refresh(self):
        name = self.location.nickname
        count = self.location.products.count()
        tree = SupplierLocationTree(name, count, str(self.location.pk))
        for sub in Product.__subclasses__():
            self.__looper(sub, tree)
        self.tree = tree.serialize()
        self.save()



        # self_pks = self.products.values('product__pk')
        # ret_dict = [{
        #     'name': dep._meta.verbose_name_plural.title(),
        #     'count': dep.objects.filter(pk__in=self_pks).count()
        # } for dep in get_departments()]


    # def __refresh_product_tree(self):
    #     name = Product._meta.verbose_name_plural.lower().strip()
    #     count = Product.objects.count()
    #     tree_product = Tree(name, count)
    #     for sub in Product.__subclasses__():
    #         Tree.loop_product(sub, tree_product)
    #     serialized = tree_product.serialize()
    #     self.product_tree = serialized
    #     self.save()


    # def __refresh_supplier_tree(self):
    #     name = 'suppliers'
    #     sups = SupplierLocation.objects.all()
    #     count = sups.count()
    #     sup_tree = Tree(name, count)
    #     for sub in Product.__subclasses__():
    #         Tree.loop_supplier(sub, sup_tree)
    #     serialized = sup_tree.serialize()
    #     self.supplier_tree = serialized
    #     self.save()

    # def product_count(self):
    #     return self.products.count()

    # def product_types(self):
    #     from config.globals import get_departments
    #     self_pks = self.products.values('product__pk')
    #     ret_dict = [{
    #         'name': dep._meta.verbose_name_plural.title(),
    #         'count': dep.objects.filter(pk__in=self_pks).count()
    #     } for dep in get_departments()]
    #     return ret_dict