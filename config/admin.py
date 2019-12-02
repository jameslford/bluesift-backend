from django.contrib import admin
from .models import LibraryLink, UserTypeStatic, UserFeature

# Register your models here.
admin.site.register(LibraryLink)
admin.site.register(UserTypeStatic)
admin.site.register(UserFeature)

