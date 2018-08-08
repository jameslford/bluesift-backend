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

class CustomerProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProduct
        fields = ('application', 'product', 'project', 'id')



class CustomerProjectSerializer(serializers.ModelSerializer):
    customer_products = CustomerProductSerializer(many=True)
    class Meta:
        model = CustomerProject
        fields = ('owner', 'address', 'nickname', 'id', 'customer_product')



