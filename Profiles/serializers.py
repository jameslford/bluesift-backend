from rest_framework import serializers
from .models import( 
                    CompanyAccount, 
                    CompanyShippingLocation, 
                    SupplierProduct, 
                    CustomerProfile, 
                    CustomerProject, 
                    CustomerProduct
                    )

class ShippingLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyShippingLocation
        fields = ('company_account','approved_seller','nickname', 'address', 'id')


class CustomerProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProject
        fields = ('owner', 'address', 'nickname', 'id')



class CustomerProductSerializer(serializers.Serializer):
    id = serializers.ReadOnlyField()
    product_id = serializers.IntegerField()
    use = serializers.CharField()
    name = serializers.CharField(max_length=120)
    image = serializers.ImageField()
    lowest_price = serializers.DecimalField(max_digits=7, decimal_places=2)
    is_priced = serializers.BooleanField()
    product_type = serializers.CharField(max_length=120)
    prices = serializers.ListField()

class SupplierProductSerializer(serializers.Serializer):
    # supplier product fields
    id = serializers.ReadOnlyField()
    name = serializers.CharField(max_length=120)
    units_available = serializers.IntegerField(default=0)
    units_per_order = serializers.DecimalField(max_digits=10, decimal_places=2, default=0)
    my_price = serializers.DecimalField( max_digits=8, decimal_places=2)
    for_sale = serializers.BooleanField(default=False)
    price_per_unit  = serializers.DecimalField( max_digits=8, decimal_places=2)
    # product fields
    product_id = serializers.IntegerField()
    product_type = serializers.CharField(max_length=120)
    image = serializers.ImageField()
    is_priced = serializers.BooleanField()
    prices = serializers.ListField()
    lowest_price = serializers.DecimalField(max_digits=7,decimal_places=2)




