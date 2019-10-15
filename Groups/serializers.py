from Addresses.serializers import AddressSerializer
from Addresses.models import Address
from UserProductCollections.models import RetailerLocation
from Profiles.serializers import serialize_profile
from Plans.serializers import PlanSerializer
from .models import RetailerCompany, ProCompany


class BusinessSerializer:

    def __init__(self, business, full=True):
        self.business = business
        self.full = full

        self.pk = business.pk
        self.address: Address = None
        self.address_string: str = None
        self.coordinates = None
        self.email = None
        self.employees = []
        self.info = None
        self.image = None
        self.locations = []
        self.location_manager = None
        self.name: str = None
        self.phone_number = None
        self.plan = None
        self.product_count: int = None
        self.product_types = []
        self.service_type = None

    def serialize(self):
        ret_dict = vars(self)
        del ret_dict['business']
        del ret_dict['full']
        new_dict = {k: v for k, v in ret_dict.items() if v}
        return new_dict

    def getData(self):
        if isinstance(self.business, RetailerLocation):
            business: RetailerLocation = self.business
            self.coordinates = business.coordinates()
            self.email = business.email
            self.product_count = business.product_count()
            self.phone_number = business.phone_number
            self.name = business.nickname
            self.image = business.image
            self.address_string = business.address_string()
            if self.full:
                self.info = business.company.info
                self.address = AddressSerializer(business.address).data
                self.product_types = business.product_types()
                if business.local_admin:
                    self.location_manager = serialize_profile(business.local_admin.user)
            return self.serialize()
        if isinstance(self.business, RetailerCompany):
            ret_company: RetailerCompany = self.business
            self.address = AddressSerializer(ret_company.business_address).data
            self.name = ret_company.name
            self.employees = [serialize_profile(employee.user) for employee in ret_company.get_employees()]
            self.phone_number = ret_company.phone_number
            self.address_string = ret_company.business_address.address_string
            self.info = ret_company.info
            self.image = ret_company.image
            self.plan = PlanSerializer(ret_company.plan).data if ret_company.plan else None
            if self.full:
                locations = RetailerLocation.objects.select_related(
                    'address',
                    'address__postal_code',
                    'company',
                    'local_admin'
                ).filter(company=ret_company)
            self.locations = [BusinessSerializer(loc).getData() for loc in locations]
            return self.serialize()
        if isinstance(self.business, ProCompany):
            pro_comp: ProCompany = self.business
            self.name = pro_comp.name
            self.service_type = pro_comp.service.label
            self.address = AddressSerializer(pro_comp.business_address).data
            self.address_string = pro_comp.business_address.address_string
            self.coordinates = [
                pro_comp.business_address.lat,
                pro_comp.business_address.lng
                ]
            self.phone_number = pro_comp.phone_number
            self.image = pro_comp.image
            self.info = pro_comp.info
            self.plan = PlanSerializer(pro_comp.plan).data if pro_comp.plan else None
            self.employees = [serialize_profile(employee.user) for employee in pro_comp.get_employees()]
            return self.serialize()
        raise AttributeError('invalid model for business argument')
