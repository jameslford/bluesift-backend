from django.db.models import Exists, OuterRef
from Addresses.serializers import AddressSerializer
from Addresses.models import Address
from Accounts.models import User
from Accounts.serializers import user_serializer
from Retailers.models import RetailerLocation, RetailerProduct
from Profiles.models import RetailerEmployeeProfile, ConsumerProfile, ProEmployeeProfile
from Projects.models import Project, Project, LibraryProduct
from Plans.serializers import PlanSerializer
from Groups.models import RetailerCompany, ProCompany, ConsumerLibrary
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
        if isinstance(self.business, RetailerLocation):
            business: RetailerLocation = self.business
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
        if isinstance(self.business, RetailerCompany):
            ret_company: RetailerCompany = self.business
            self.address = AddressSerializer(ret_company.business_address).data
            self.name = ret_company.name
            self.business_type = BusinessType.RETAILER_COMPANY.value
            self.employees = ret_company.get_employees()
            # self.employees = [ProfileSerializer(employee.user).data for employee in ret_company.get_employees()]
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
            self.business_type = BusinessType.PRO_COMPANY.value
            self.service_type = pro_comp.service.label
            self.address = AddressSerializer(pro_comp.business_address).data
            self.address_string = pro_comp.business_address.address_string
            self.phone_number = pro_comp.phone_number
            self.image = pro_comp.image
            self.info = pro_comp.info
            self.plan = PlanSerializer(pro_comp.plan).data if pro_comp.plan else None
            # self.employees = [ProfileSerializer(employee.user).data for employee in pro_comp.get_employees()]
            return self.serialize()
        if isinstance(self.business, ConsumerLibrary):
            return
            # con_lib: ConsumerLibrary = self.business
            # self.plan = PlanSerializer(con_lib.plan).data if con_lib.plan else None
            # return self.serialize()
        raise AttributeError('invalid model for business argument')

class ProfileSerializer:

    def __init__(self, user: User):
        if user:
            self.user = user
            self.profile = user.get_profile()

        self.pk = None
        self.avatar: str = None
        self.user_type: str = None
        self.company_name: str = None
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

        if isinstance(self.profile, ProEmployeeProfile):
            self.user_type = 'pro'
            self.admin = self.profile.admin
            self.owner = self.profile.owner
            self.title = self.profile.title
            if full:
                self.group = BusinessSerializer(self.user.get_group()).getData()
                self.tasks = self.profile.bid_assignments.all()
        if isinstance(self.profile, RetailerEmployeeProfile):
            self.user_type = 'retailer'
            self.admin = self.profile.admin
            self.owner = self.profile.owner
            self.title = self.profile.title
            if full:
                self.group = BusinessSerializer(self.user.get_group()).getData()
        if isinstance(self.profile, ConsumerProfile):
            self.user_type = 'user'
            if full:
                # self.group = BusinessSerializer(self.user.get_group()).getData()
                self.plan = PlanSerializer(self.profile.group.plan).data if self.profile.group.plan else None

        self.user = user_serializer(self.user) if self.user.is_authenticated else None

    def get_dict(self):
        return {
            'pk': self.pk,
            'user': self.user,
            'avatar': self.avatar,
            'user_type': self.user_type,
            'company_name': self.company_name,
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

    def __init__(self, nickname=None, pk=None, remove=None):
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
        # selected_location: PLShort = None

    def return_data(self):
        return {
            'count': self.count,
            'product_ids': self.product_ids,
            'pl_short_list': self.pl_short_list,
            'selected_location': self.selected_location
            }


    def retrieve_data(self):
        collection = None
        if self.user.is_authenticated:
            collections = self.user.get_collections()
            self.pl_short_list = [CollectionNote(res).data for res in list(collections.values('nickname', 'pk'))]
            collection = collections.get(pk=self.pk) if self.pk else collections.first()
        if collection:
            self.product_ids = collection.products.values_list('product__pk', flat=True)
            self.selected_location = CollectionNote(collection.nickname, collection.pk).serialize()
        else:
            self.product_ids = []
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
            collections = RetailerLocation.objects.prefetch_related('products').filter(company=group)
            subquery = RetailerProduct.objects.filter(retailer=OuterRef('pk'))
            res = collections.annotate(removed=Exists(subquery)).values('nickname', 'pk', 'removed')
            self.pl_list = [CollectionNote(col['nickname'], col['pk'], not col['removed']).serialize() for col in res]
        else:
            remove = group.products.filter(pk=self.pk).exists()
            self.pl_list.append(CollectionNote('workbench', None, remove).serialize())
        # elif self.user.is_pro:
            # collections = Project.objects.prefetch_related('products').filter(owner=group)
            # subquery = Pro.objects.filter(project=OuterRef('pk'))
        # else:
        #     collections = Project.objects.prefetch_related('products').filter(owner=group)
        #     subquery = LibraryProduct.objects.filter(project=OuterRef('pk'))
        # self.pl_list =


    @property
    def data(self):
        self.retrieve_data()
        return self.pl_list






# @api_view(['GET'])
# def pl_status_for_product(request: HttpRequest, pk):
#     pl_list = PLStatusList(pl_list=[])
#     if not request.user.is_authenticated:
#         return Response(asdict(pl_list), status=status.HTTP_200_OK)
#     product = Product.objects.get(pk=pk)
#     collections = request.user.get_collections()
#     for collection in collections:
#         remove = product.pk in collection.products.values_list('product__pk', flat=True)
#         plmed = PLMedium(collection.nickname, collection.pk, remove)
#         pl_list.pl_list.append(plmed)
#     return Response(asdict(pl_list), status=status.HTTP_200_OK)



# @dataclass
# class PLShort:
#     nickname: str
#     pk: int


# @dataclass
# class PLMedium(PLShort):
#     remove: bool


# @dataclass
# class PLStatusList:
#     pl_list: List[PLMedium]


# @dataclass
# class ShortLib:
#     count: int
#     product_ids: List[str]
#     pl_short_list: List[PLShort]
#     selected_location: PLShort = None
