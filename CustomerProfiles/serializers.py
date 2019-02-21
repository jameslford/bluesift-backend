from rest_framework import serializers
from Addresses.serializers import AddressSerializer
from Addresses.models import Address, Zipcode
# from Addresses.models import Address
from .models import CustomerProfile, CustomerProduct, CustomerProject, CustomerProjectApplication
from Products.serializers import ProductDetailSerializer


class CustomerProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(read_only=True, many=True)

    class Meta:
        model = CustomerProfile
        fields = (
            'phone_number',
            'addresses',
            'plan'
            )


class CustomerLibrarySerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()

    class Meta:
        model = CustomerProfile
        fields = (
            'name',
            'plan',
            'projects',
        )

    def get_projects(self, instance):
        projects = CustomerProject.objects.select_related('address').filter(owner=instance)
        return CustomerProjectSerializer(projects, many=True).data


class CustomerProjectSerializer(serializers.ModelSerializer):
    address = AddressSerializer(required=False)

    class Meta:
        model = CustomerProject
        fields = (
            'address',
            'nickname',
            'id',
            )

    def create(self, profile, validated_data):
        address = validated_data.pop('address', None)
        address_object = None
        if address:
            zipcode = address.pop('postal_code', None)
            zipcode = Zipcode.objects.create(code=zipcode).first()
            if not zipcode:
                return 'Invalid Zip'
            address_object = Address.objects.create(postal_code=zipcode, **address)
        nickname = validated_data.get('nickname')
        project = CustomerProject(owner=profile, nickname=nickname)
        if address_object:
            project.address = address_object
        project.save()
        return project


class CustomerProductSerializer(serializers.ModelSerializer):
    product = ProductDetailSerializer(required=False)

    class Meta:
        model = CustomerProduct
        fields = (
            'id',
            'product',
            )


class CustomerProjectApplicationSerializer(serializers.ModelSerializer):
    # products = CustomerProductSerializer(many=True)

    class Meta:
        model = CustomerProjectApplication
        fields = (
            'id',
            'label',
            'products'
        )

    def update(self, instance, validated_data):
        label = validated_data.pop('label', instance.label)
        instance.label = label

        products = validated_data.pop('products', instance.products)
        instance.products.clear()
        instance.products.add(*products)
        instance.save()
        # return instance







class CustomerProjectDetailSerializer(serializers.ModelSerializer):
    products = CustomerProductSerializer(many=True)
    applications = CustomerProjectApplicationSerializer(many=True)

    class Meta:
        model = CustomerProject
        fields = (
            'id',
            'applications',
            'address',
            'nickname',
            'products'
            )
