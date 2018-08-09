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
    id              = serializers.ReadOnlyField()
    product_id      = serializers.IntegerField()
    use             = serializers.CharField()
    name            = serializers.CharField(max_length=120)
    image           = serializers.ImageField()
    lowest_price    = serializers.DecimalField(max_digits=7,decimal_places=2)
    is_priced       = serializers.BooleanField()
    product_type    = serializers.CharField(max_length=120)
    prices          = serializers.ListField()



# product.use,
# product.product.name,
# product.product.image,
# product.product.id,   
# product.id,
# product.product.prices(),
# product.product.lowest_price,
# product.product.is_priced,
# product.product.product_type

# serializer['id'] = product.use,
# serializer['product_id'] = product.product.name,
# serializer['use'] = product.product.image,
# serializer['name'] = product.product.id,   
# serializer['image'] = product.id,
# serializer['lowest_price'] = product.product.prices(),
# serializer['is_priced'] = product.product.lowest_price,
# serializer['product_type'] = product.product.is_priced,
# serializer['prices'] = product.product.product_type