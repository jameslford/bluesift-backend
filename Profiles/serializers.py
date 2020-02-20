
def serialize_profile(profile):
    return {
        'avatar' : profile.avatar.url if profile.avatar else None,
        # 'user_type' : profile.user_type,
        # 'group_name' : profile.group_name,
        'owner' : profile.owner,
        'admin' : profile.admin,
        'title' : profile.title,
        # 'plan' : profile.plan,
        # 'phone_number' : profile.phone_number,
        }



# class ProfiletasksSerializer:
#     def __inigroupt__(self, profile):
#         self.avatar: str = None
#         self.user_type: str = None
#         self.group_name: str = None
#         self.owner = False
#         self.admin = False
#         self.title = False
#         self.plan = None
#         self.phone_number = None
#         self.tasks = []
#         self.collections = None
#         self.group = None


#     def retrieve_values(self, full=False):
#         self.pk = self.profile.pk
#         self.avatar = self.profile.avatar.url if self.profile.avatar else None
#         # self.collections = self.user.get_collections().values('pk', 'nickname')

#         self.library_links = self.user.get_library_links()

#         if isinstance(self.profile, SupplierEmployeeProfile):
#             self.user_type = 'retailer'
#             self.admin = self.profile.admin
#             self.owner = self.profile.owner
#             self.title = self.profile.title
#             self.group_name = self.user.get_group().name
#             if full:
#                 self.group = BusinessSerializer(self.user.get_group()).getData()
#         if isinstance(self.profile, ConsumerProfile):
#             self.user_type = 'user'
#             self.group_name = self.user.get_first_name() if self.user else None
#             if full:
#                 self.plan = PlanSerializer(self.profile.plan).data if self.profile.plan else None

#         self.user = user_serializer(self.user) if self.user.is_authenticated else None

#     def get_dict(self):
#         return {
#             'pk': self.pk,
#             'user': self.user,
#             'avatar': self.avatar,
#             'user_type': self.user_type,
#             'group_name': self.group_name,
#             'owner': self.owner,
#             'admin': self.admin,
#             'title': self.title,
#             'plan': self.plan,
#             'phone_number': self.phone_number,
#             'tasks': self.tasks,
#             'libraryLinks': self.library_links,
#             'group': self.group,
#             'collections': self.collections,
#             }

#     @property
#     def data(self):
#         if self.profile:
#             self.retrieve_values()
#         return self.get_dict()

#     @property
#     def full_data(self):
#         if self.profile:
#             self.retrieve_values(True)
#         return self.get_dict()