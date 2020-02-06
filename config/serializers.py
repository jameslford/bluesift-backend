from django.db.models import Exists, OuterRef
from Addresses.serializers import AddressSerializer
from Addresses.models import Address
from Accounts.models import User
from Accounts.serializers import user_serializer
from Suppliers.models import SupplierLocation, SupplierProduct
from Profiles.models import SupplierEmployeeProfile, ConsumerProfile
# from Profiles.models import LibraryProduct
# from Projects.models import Project
from Plans.serializers import PlanSerializer
from Groups.models import SupplierCompany
from .globals import BusinessType


class BusinessSerializer:

    def __init__(self, business, full=True):
        self.business = business
        self.business_type = None
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
        if isinstance(self.business, SupplierLocation):
            business: SupplierLocation = self.business
            self.business_type = BusinessType.RETAILER_LOCATION.value
            self.email = business.email
            self.product_count = business.product_count()
            self.phone_number = business.phone_number
            self.name = business.nickname
            self.image = business.image.url if business.image else None
            self.address = AddressSerializer(business.address).data
            self.address_string = business.address_string()
            self.product_types = business.product_types()
            if self.full:
                self.info = business.company.info
                if business.local_admin:
                    self.location_manager = ProfileSerializer(business.local_admin.user).data
            return self.serialize()
        if isinstance(self.business, SupplierCompany):
            ret_company: SupplierCompany = self.business
            self.address = AddressSerializer(ret_company.business_address).data
            self.name = ret_company.name
            self.business_type = BusinessType.RETAILER_COMPANY.value
            self.employees = ret_company.get_employees()
            self.phone_number = ret_company.phone_number
            self.address_string = ret_company.business_address.address_string
            self.info = ret_company.info
            self.image = ret_company.image
            self.plan = PlanSerializer(ret_company.plan).data if ret_company.plan else None
            if self.full:
                locations = SupplierLocation.objects.select_related(
                    'address',
                    'address__postal_code',
                    'company',
                    'local_admin'
                ).filter(company=ret_company)
                self.locations = [BusinessSerializer(loc).getData() for loc in locations]
            return self.serialize()
        return


class ProfileSerializer:

    def __init__(self, user: User):
        self.user: User = None
        self.profile = None

        if user.is_authenticated:
            self.user = user
            self.profile = user.get_profile()

        self.pk = None
        self.avatar: str = None
        self.user_type: str = None
        self.group_name: str = None
        self.owner = False
        self.admin = False
        self.title = False
        self.plan = None
        self.phone_number = None
        self.tasks = []
        self.collections = None
        self.group = None
        self.library_links = None


    def retrieve_values(self, full=False):
        self.pk = self.profile.pk
        self.avatar = self.profile.avatar.url if self.profile.avatar else None
        self.collections = self.user.get_collections().values('pk', 'nickname')
        self.library_links = self.user.get_library_links()

        if isinstance(self.profile, SupplierEmployeeProfile):
            self.user_type = 'retailer'
            self.admin = self.profile.admin
            self.owner = self.profile.owner
            self.title = self.profile.title
            self.group_name = self.user.get_group().name
            if full:
                self.group = BusinessSerializer(self.user.get_group()).getData()
        if isinstance(self.profile, ConsumerProfile):
            self.user_type = 'user'
            self.group_name = self.user.get_first_name() if self.user else None
            if full:
                self.plan = PlanSerializer(self.profile.plan).data if self.profile.plan else None

        self.user = user_serializer(self.user) if self.user.is_authenticated else None

    def get_dict(self):
        return {
            'pk': self.pk,
            'user': self.user,
            'avatar': self.avatar,
            'user_type': self.user_type,
            'group_name': self.group_name,
            'owner': self.owner,
            'admin': self.admin,
            'title': self.title,
            'plan': self.plan,
            'phone_number': self.phone_number,
            'tasks': self.tasks,
            'libraryLinks': self.library_links,
            'group': self.group,
            'collections': self.collections,
            }

    @property
    def data(self):
        if self.profile:
            self.retrieve_values()
        return self.get_dict()

    @property
    def full_data(self):
        if self.profile:
            self.retrieve_values(True)
        return self.get_dict()


class CollectionNote:

    def __init__(self, nickname='library', pk=None, remove=None):
        self.nickname = nickname
        self.pk = pk
        self.remove = remove

    def serialize(self):
        return {
            'nickname': self.nickname,
            'pk': self.pk,
            'remove': self.remove
            }

    @property
    def data(self):
        return self.serialize()


class ShortLib:

    def __init__(self, user, pk=None):
        self.user = user
        self.pk = pk
        self.count: int = None
        self.product_ids = None
        self.pl_short_list = None
        self.selected_location = None

    def return_data(self):
        return {
            'count': self.count,
            'product_ids': self.product_ids,
            'pl_short_list': self.pl_short_list,
            'selected_location': self.selected_location
            }


    def retrieve_data(self):
        collection = None
        self.product_ids = []
        self.selected_location = CollectionNote().serialize()
        if not self.user.is_authenticated:
            return
        if self.user.is_supplier:
            collections = self.user.get_collections()
            self.pl_short_list = [CollectionNote(res).data for res in list(collections.values('nickname', 'pk'))]
            collection = collections.get(pk=self.pk) if self.pk else collections.first()
            self.product_ids = collection.products.values_list('product__pk', flat=True)
            self.selected_location = CollectionNote(collection.nickname, collection.pk).serialize()
            return
        group = self.user.get_group()
        self.product_ids = list(group.products.all().values_list('pk', flat=True))
        self.selected_location = CollectionNote().serialize()


    @property
    def data(self):
        self.retrieve_data()
        return self.return_data()


class ProductStatus:

    def __init__(self, user: User, pk):
        self.user = user
        self.pk = pk
        self.pl_list = []

    def retrieve_data(self):
        if not self.user.is_authenticated or not self.pk:
            return
        group = self.user.get_group()
        if self.user.is_supplier:
            collections = SupplierLocation.objects.prefetch_related('products').filter(company=group)
            subquery = SupplierProduct.objects.filter(retailer=OuterRef('pk'))
            res = collections.annotate(removed=Exists(subquery)).values('nickname', 'pk', 'removed')
            self.pl_list = [CollectionNote(col['nickname'], col['pk'], not col['removed']).serialize() for col in res]
        else:
            remove = group.products.filter(product__pk=self.pk).exists()
            self.pl_list.append(CollectionNote('workbench', None, remove).serialize())

    @property
    def data(self):
        self.retrieve_data()
        return self.pl_list
