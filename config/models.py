'''
These models hold/relay static materials served for front end
'''

from xml.dom import minidom
from model_utils import Choices
from django.db import models
from django.contrib.postgres.fields import JSONField
from utils.tree import Tree
from Products.models import Product
from Suppliers.models import SupplierLocation


class ConfigTree(models.Model):
    ''' singleton used for navigations and counts on user GUI. to be refreshed daily '''
    product_tree = JSONField(null=True)
    supplier_tree = JSONField(null=True)


    def save(self, *args, **kwargs):
        self.pk = 1
        super(ConfigTree, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    @classmethod
    def refresh(cls):
        tree = cls.load()
        tree.__refresh_product_tree()
        tree.__refresh_supplier_tree()

    def __loop_product(self, current: object, parent):
        if not current._meta.abstract:
            name = current._meta.verbose_name_plural.lower().strip()
            count = current.objects.count()
            new_tree = Tree(name, count)
            parent.children.append(new_tree)
            for sub in current.__subclasses__():
                self.__loop_product(sub, new_tree)
        else:
            for child in current.__subclasses__():
                self.__loop_product(child, parent)

    def __loop_supplier(self, current: object, parent):
        if not current._meta.abstract:
            name = current._meta.verbose_name_plural.lower().strip()
            supplier_product_pks = current.objects.values('priced__location__pk').distinct()
            count = SupplierLocation.objects.filter(pk__in=supplier_product_pks).count()
            new_tree = Tree(name, count)
            parent.children.append(new_tree)
            for sub in current.__subclasses__():
                self.__loop_product(sub, new_tree)
        else:
            for child in current.__subclasses__():
                self.__loop_product(child, parent)

    def __refresh_product_tree(self):
        name = Product._meta.verbose_name_plural.lower().strip()
        count = Product.objects.count()
        tree_product = Tree(name, count)
        for sub in Product.__subclasses__():
            self.__loop_product(sub, tree_product)
        serialized = tree_product.serialize()
        self.product_tree = serialized
        self.save()


    def __refresh_supplier_tree(self):
        name = 'suppliers'
        sups = SupplierLocation.objects.all()
        count = sups.count()
        sup_tree = Tree(name, count)
        for sub in Product.__subclasses__():
            self.__loop_supplier(sub, sup_tree)
        serialized = sup_tree.serialize()
        self.supplier_tree = serialized
        self.save()



class LibraryLink(models.Model):
    '''
    Holds svg paths (draw_path), descriptions and labels for user libraries.
    uses for_user/retailer/pro to serve the correct links per user accordingly
    '''
    TYPES = Choices(
        'admin',
        'company_info',
        'all_collaborators',
        'all_materials',
        'projects',
        'locations',
        'profile',
        )
    label = models.CharField(max_length=18, unique=True)
    link = models.CharField(max_length=18, default='')
    description = models.CharField(max_length=60, blank=True, null=True)
    draw_path = models.TextField(blank=True, null=True)
    display = models.FileField(upload_to='misc/', blank=True, null=True)
    include_collections = models.BooleanField(default=False)
    for_user = models.BooleanField(default=False)
    for_supplier = models.BooleanField(default=False)
    for_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.link:
            self.link = self.label
        if not self.display:
            super().save(*args, **kwargs)
            return
        o_file = self.display
        doc = minidom.parse(o_file)
        paths = doc.getElementsByTagName('path')
        for path in paths:
            path_id = path.getAttribute('id')
            if path_id == 'drawPath':
                self.draw_path = path.getAttribute('d')
                break
        super().save(*args, **kwargs)

    def custom_serialize(self):
        return {
            'label': self.label,
            'link': self.link,
            'icon': self.draw_path,
            'description': self.description,
            'includeCollections': self.include_collections
            }


# TODO convert this to script
    @classmethod
    def create_links(cls):
        admin = cls.objects.get_or_create(label='admin')[0]
        admin.for_admin = True
        admin.save()

        company_info = cls.objects.get_or_create(label='company_info')[0]
        company_info.for_supplier = True
        company_info.save()

        profile = cls.objects.get_or_create(label='profile')[0]
        profile.for_admin = True
        profile.for_supplier = True
        profile.for_user = True
        profile.save()

        palette = cls.objects.get_or_create(label='palette')[0]
        palette.for_user = True
        palette.save()

        locations = cls.objects.get_or_create(label='locations')[0]
        locations.for_supplier = True
        locations.include_collections = True
        locations.save()

        projects = cls.objects.get_or_create(label='projects')[0]
        projects.for_user = True
        projects.include_collections = True
        projects.save()


class UserFeature(models.Model):
    label = models.CharField(max_length=40, unique=True)
    description = models.CharField(max_length=60, blank=True, null=True)
    draw_path = models.TextField(blank=True, null=True)
    display = models.FileField(upload_to='misc/', blank=True, null=True)

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if not self.display:
            super().save(*args, **kwargs)
            return
        o_file = self.display
        doc = minidom.parse(o_file)
        paths = doc.getElementsByTagName('path')
        for path in paths:
            path_id = path.getAttribute('id')
            if path_id == 'drawPath':
                self.draw_path = path.getAttribute('d')
                break
        super().save(*args, **kwargs)

    def serialize(self):
        return {
            'label': self.label,
            'description': self.description,
            'draw_path': self.draw_path
        }


class UserTypeStatic(models.Model):
    '''
    Serves pictures and descriptions etc. to inform user of usertypes on landing page
    '''

    label = models.CharField(max_length=20, unique=True)
    short_description = models.CharField(max_length=150, blank=True, null=True)
    display_image = models.ImageField(max_length=1000, upload_to='misc/', blank=True, null=True)
    tagline = models.CharField(max_length=300, blank=True, null=True)
    full_text = models.TextField(blank=True, null=True)
    feature = models.ManyToManyField(UserFeature, related_name='ut_static', blank=True)
    include_options = models.BooleanField(default=False)

    def __str__(self):
        return self.label

    def serialize(self):
        return {
            'label': self.label,
            'short_description': self.short_description,
            'image': self.display_image.url if self.display_image else None,
            'tagline': self.tagline,
            'full_text': self.full_text,
            'features': [feat.serialize() for feat in self.feature.all()],
            'options': ['owner', 'admin', 'employee'] if self.include_options else None
            }
