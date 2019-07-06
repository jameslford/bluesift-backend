from rest_framework import serializers
from Addresses.serializers import AddressSerializer, AddressUpdateSerializer
from Addresses.models import Address, Zipcode
from Groups.models import CompanyAccount



class CompanyAccountSerializer(serializers.ModelSerializer):
    address = AddressSerializer(read_only=True)

    class Meta:
        model = CompanyAccount
        fields = ('name', 'phone_number', 'address')


class CompanyAccountDetailSerializer(serializers.ModelSerializer):
    headquarters = AddressSerializer()
    locations = serializers.SerializerMethodField()
    employees = serializers.SerializerMethodField()

    class Meta:
        model = CompanyAccount
        fields = (
            'pk',
            'headquarters',
            'phone_number',
            'name',
            'shipping_location_count',
            'plan',
            'employees',
            'locations'
        )

    def get_locations(self, instance):
        response_list = []
        employee = self.context.get('employee')
        locations = CompanyShippingLocation.objects.select_related(
            'local_admin',
            'company_account',
            'address',
            'address__postal_code',
            'address__coordinates'
             ).filter(company_account=instance)
        if not locations:
            locations = CompanyShippingLocation.objects.create(company_account=instance)
        for location in locations:
            response_list.append(ShippingLocationListSerializer(location, context={'employee': employee}).data)
        return response_list

    def get_employees(self, instance):
        employees = instance.employees.all()
        return EmployeeProfileSerializer(employees, many=True).data
        # return ShippingLocationListSerializer(locations, many=True, context={'user': user}).data