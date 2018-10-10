from django.db import models
from django.conf import settings
from Addresses.models import Address
from Products.models import Product
from djmoney.models.fields import MoneyField
import decimal



class CompanyAccount(models.Model):
    name = models.CharField(max_length=120)
    account_owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        limit_choices_to={'is_supplier' : True},
        related_name='company_account'
        )
    headquarters = models.ForeignKey(Address, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        if self.name:
            return self.name
        else:
            return self.account_owner.get_first_name() + "'s Company"



class CompanyShippingLocation(models.Model):
    company_account = models.ForeignKey(
        CompanyAccount,
        on_delete=models.CASCADE,
        related_name='shipping_locations'
        )
    address = models.ForeignKey(Address, null=True, on_delete=models.CASCADE)
    nickname = models.CharField(max_length=120, null=True, blank=True)
    approved_seller = models.BooleanField(default=False)
    number = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return str(self.company_account) + ' ' + str(self.number)

    def assign_number(self):
        account = self.company_account
        count = account.shipping_locations.all().count()
        number = count + 1
        return number

    def save(self, *args, **kwargs):
        self.number = self.assign_number()
        if not self.nickname:
            self.nickname = self.company_account.name + ' ' + str(self.number)
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
    price_per_unit = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    units_available = models.IntegerField(default=0, null=True)
    units_per_order = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    for_sale = models.BooleanField(default=False)

    def __str__(self):
        return str(self.supplier) + ' ' + str(self.product.name)

    def product_name(self):
        return self.product.name

    def product_category(self):
        return self.product.build.category.label

    def product_build(self):
        return self.product.build.label

    def product_material(self):
        return self.product.material.label

    def product_image(self):
        return str(self.product.image.image.url)

    def product_lowest_price(self):
        return str(self.product.lowest_price)

    def set_price(self):
        if self.my_price:
            self.price_per_unit = self.my_price * decimal.Decimal(1.10)

    def save(self, *args, **kwargs):
        self.set_price()
        if self.for_sale:
            if self.units_available <= 0:
                self.for_sale = False
            if self.supplier.approved_seller is False:
                self.for_sale = False
        super(SupplierProduct, self).save(*args, **kwargs) # Call the real save() method
        self.product.prices()

    class Meta:
        unique_together = ('product', 'supplier')


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.CASCADE,
        related_name='user_profile'
        )
    addresses = models.ManyToManyField(Address, related_name='addresses')
    phone_number = models.IntegerField(null=True)
    name = models.CharField(max_length=40, blank=True, null=True)

    def __str__(self):
        return self.user.get_first_name() + "'s library"



class CustomerProject(models.Model):
    owner = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name='projects'
        )
    address = models.ForeignKey(
        Address,
        null=True,
        on_delete=models.SET_NULL,
        related_name='projects'
        )
    nickname = models.CharField(max_length=50)

    def __str__(self):
        if self.nickname:
            return self.nickname
        else:
            return self.owner.user.get_first_name()

class CustomerProduct(models.Model):
    use = models.CharField(max_length=100, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='customer_products')
    project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, related_name='products')

    def __str__(self):
        return self.product.name

    def product_id(self):
        return self.product.id

    def product_name(self):
        return self.product.name

    def product_category(self):
        return self.product.build.category.label

    def product_build(self):
        return self.product.build.label

    def product_material(self):
        return self.product.material.label

    def product_image(self):
        return str(self.product.image.image.url)

    def product_lowest_price(self):
        return str(self.product.lowest_price)

    def product_for_sale(self):
        return self.product.for_sale

    def product_prices(self):
        return self.product.prices()
