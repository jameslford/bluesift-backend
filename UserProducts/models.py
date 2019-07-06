from django.db import models



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

    class Meta:
        unique_together = ('product', 'supplier')

    def __str__(self):
        return str(self.supplier) + ' ' + str(self.product.name)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.check_approvals()
        self.check_availability()
        self.product.set_locations()
        return super().save(force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

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
            self.publish_in_store_price = False

    def check_approvals(self):
        if not self.supplier.approved_online_seller:
            self.publish_online_price = False
        if not self.supplier.approved_in_store_seller:
            self.publish_in_store_price = False
            self.publish_in_store_availability = False
