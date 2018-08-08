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

# class CustomerProductSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CustomerProduct
#         fields = ('application', 'product', 'project', 'id')



class CustomerProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProject
        fields = ('owner', 'address', 'nickname', 'id')



class CustomerProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=150)
    application = serializers.CharField(max_length=150)
    