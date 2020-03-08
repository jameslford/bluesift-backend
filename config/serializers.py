from django.db.models import Exists, OuterRef
from Addresses.serializers import AddressSerializer
from Addresses.models import Address
from Accounts.models import User
from Suppliers.models import SupplierLocation, SupplierProduct
from Plans.serializers import PlanSerializer
from Groups.models import SupplierCompany
from utils.tree import Tree
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
            self.product_count = business.products.count()
            self.phone_number = business.phone_number
            self.name = business.nickname
            self.image = business.image.url if business.image else None
            self.address = AddressSerializer(business.address).data
            self.info = business.company.info
            # self.address_string = business.address_string()
            # self.product_types = business.product_types()
            if self.full:
                self.info = business.company.info
                # if business.local_admin:
                    # self.location_manager = ProfileSerializer(business.local_admin.user).data
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


class LinkTree:
    def __init__(self, name=None, link=None, icon=None, description=None, children=None, pk=None, count=None, tree: Tree = None):
        self.name = name
        self.link = link
        self.icon = icon
        self.description = description
        self.pk = pk
        self.count = count
        # self.children = children if children else []
        self.children = []
        if children:
            self.children = [LinkTree(**child) for child in children]
        if tree:
            self.name = tree.name
            self.count = tree.count
            self.children = [LinkTree(**child) for child in tree.children]

    @property
    def serialized(self):
        return {
            'name': self.name,
            'link': self.link,
            'icon': self.icon,
            'description': self.description,
            'pk': self.pk,
            'count': self.count,
            'children': [child.serialized for child in self.children]
        }


class LinkSerializer:

    def __init__(self, user: User):
        self.avatar = None
        self.library_links = []

        if user and user.is_authenticated:
            profile = user.get_profile()
            self.avatar = profile.avatar.url if profile.avatar else None
            self.library_links = [LinkTree(name=child.label, link=child.link) for child in user.get_library_links()]
            if user.is_supplier:
                trees = [ptree['product_tree__tree'] for ptree in user.get_collections().values('product_tree__tree')]
                self.library_links.append(LinkTree(name='locations', count=None, children=trees))
            else:
                plinks = [{'name': val['nickname'], 'link': val['pk']} for val in user.get_collections().values('pk', 'nickname')]
                self.library_links.append(LinkTree(name='projects', children=plinks))

    @property
    def serialized(self):
        return [link.serialized for link in self.library_links]


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
            subquery = SupplierProduct.objects.filter(location=OuterRef('pk'))
            res = collections.annotate(removed=Exists(subquery)).values('nickname', 'pk', 'removed')
            self.pl_list = [CollectionNote(col['nickname'], col['pk'], not col['removed']).serialize() for col in res]
        else:
            remove = group.products.filter(product__pk=self.pk).exists()
            self.pl_list.append(CollectionNote('workbench', None, remove).serialize())

    @property
    def data(self):
        self.retrieve_data()
        return self.pl_list
