# from rest_framework import serializers
# from Addresses.serializers import AddressSerializer
# from Addresses.models import Address, Zipcode
# from Products.models import Product
# from Products.serializers import SerpyProduct
# from django.db.models import Subquery
# from .models import CustomerProfile, CustomerProduct, CustomerProject, CustomerProjectApplication


# class CustomerProfileSerializer(serializers.ModelSerializer):
#     addresses = AddressSerializer(read_only=True, many=True)

#     class Meta:
#         model = CustomerProfile
#         fields = (
#             'phone_number',
#             'addresses',
#             'plan'
#             )


# class CustomerLibrarySerializer(serializers.ModelSerializer):
#     projects = serializers.SerializerMethodField()

#     class Meta:
#         model = CustomerProfile
#         fields = (
#             'name',
#             'plan',
#             'projects',
#         )

#     def get_projects(self, instance):
#         projects = CustomerProject.objects.select_related('address').filter(owner=instance)
#         return CustomerProjectSerializer(projects, many=True).data


# class CustomerProjectSerializer(serializers.ModelSerializer):
#     address = AddressSerializer(required=False)

#     class Meta:
#         model = CustomerProject
#         fields = (
#             'id',
#             'address',
#             'product_count',
#             'nickname',
#             'application_count'
#             )

#     def create(self, profile, validated_data):
#         address = validated_data.pop('address', None)
#         address_object = None
#         if address:
#             zipcode = address.pop('postal_code', None)
#             zipcode = Zipcode.objects.filter(**zipcode).first()
#             if not zipcode:
#                 return 'Invalid Zip'
#             address_object = Address.objects.create(postal_code=zipcode, **address)
#         nickname = validated_data.get('nickname')
#         project = CustomerProject(owner=profile, nickname=nickname)
#         if address_object:
#             project.address = address_object
#         project.save()
#         return project


# class CustomerProductSerializer(serializers.ModelSerializer):
#     product = SerpyProduct()

#     class Meta:
#         model = CustomerProduct
#         fields = (
#             'id',
#             'product',
#             )


# class CustomerProjectApplicationSerializer(serializers.ModelSerializer):
#     # products = CustomerProductSerializer(many=True)

#     class Meta:
#         model = CustomerProjectApplication
#         fields = (
#             'id',
#             'label',
#             'products'
#         )

#     def update(self, instance, validated_data):
#         label = validated_data.pop('label', instance.label)
#         instance.label = label

#         products = validated_data.pop('products', instance.products)
#         instance.products.clear()
#         instance.products.add(*products)
#         instance.save()
#         # return instance


# class CustomerProjectDetailSerializer(serializers.ModelSerializer):
#     # products = SerpyProduct(many=True)
#     products = serializers.SerializerMethodField()
#     applications = CustomerProjectApplicationSerializer(many=True)

#     class Meta:
#         model = CustomerProject
#         fields = (
#             'pk',
#             'applications',
#             'address',
#             'nickname',
#             'products'
#             )

#     def get_products(self, instance):
#         # product_ids = self.context.get('product_ids', None)
#         products = Product.objects.select_related(
#             'manufacturer'
#         ).filter(pk__in=Subquery(instance.products.values('product__pk')))
#         products = products.product_prices()
#         return SerpyProduct(products, many=True).data
