from django.db import models
from django.db.utils import IntegrityError
from Suppliers.models import SupplierLocation
from Products.models import Product

def debug_print(*args):
    for arg in args:
        print(arg)


class SearchIndex(models.Model):
    name = models.CharField(max_length=200, unique=True)
    return_url = models.CharField(max_length=200)
    in_department = models.CharField(max_length=150, blank=True, null=True)
    hash_value = models.CharField(max_length=2000, unique=True)
    product = models.OneToOneField(
        Product,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )
    supplier_location = models.OneToOneField(
        SupplierLocation,
        on_delete=models.CASCADE,
        null=True,
        blank=True
        )


    @classmethod
    def create_or_update(cls, name, return_url, hash_value, **kwargs):
        print('--------')
        in_department = kwargs.get('in_department', '')
        name_check: SearchIndex = cls.objects.filter(name=name).first()
        if name_check:
            name_check.return_url = return_url
            name_check.hash_value = hash_value
            name_check.in_department = in_department
            name_check.save()
            debug_print(*[name, hash_value, return_url, '-----------'])
            return
        hash_check: SearchIndex = cls.objects.filter(hash_value=hash_value).first()
        if hash_check:
            hash_check.return_url = return_url
            hash_check.name = name
            hash_check.in_department = in_department
            hash_check.save()
            debug_print(*[name, hash_value, return_url, '-----------'])
            return
        cls.objects.create(
            name=name,
            return_url=return_url,
            in_department=in_department,
            hash_value=hash_value
            )
        debug_print(*[name, hash_value, return_url, '-----------'])
        return

    @classmethod
    def create_refresh_suppliers(cls):
        for sup in SupplierLocation.objects.all():
            hash = sup.get_hash_value()
            sio = SearchIndex.objects.get_or_create(
                name=sup.nickname,
                hash_value=hash,
                supplier_location=sup,
                return_url='business-detail/' + str(sup.pk),
                in_department='suppliers'
                )[0]
            print(sio.name)


            # print('others = ', others.nickname)
            # try:
            #     sio = cls.objects.get_or_create(supplier_location=sup)[0]

            #     sio.name = sup.nickname
            #     debug_print(*[sio.name, sio.hash_value, sio.return_url, '-----------'])
            #     sio.save()
            # except IntegrityError as e:
            #     print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            #     print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            #     print(sup.nickname)
            #     print(sup.get_hash_value())
            #     print(e)
            #     print(e.__cause__)
            #     print('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            #     continue


    @classmethod
    def create_refresh_products(cls):
        for sup in Product.subclasses.all().select_subclasses():
            try:
                sio = cls.objects.get_or_create(product=sup)[0]
                sio.name = sup.get_name()
                sio.hash_value = sup.get_hash_value()
                sio.return_url = 'product-detail/' + str(sup.pk)
                sio.in_department = sup._meta.verbose_name_plural
                debug_print(*[sio.name, sio.hash_value, sio.return_url, '-----------'])
                sio.save()
            except IntegrityError:
                continue







# class CAtegoricalIndex(models.Model):
#     name = models.CharField(max_length=200, unique=True)
#     return_url = models.CharField(max_length=200)
#     in_department = models.CharField(max_length=150, blank=True, null=True)
#     hash_value = models.CharField(max_length=2000, unique=True)
#     selected_count = models.IntegerField(default=0)


#     @classmethod
#     def create_or_update(cls, name, return_url, hash_value, **kwargs):
#         print('--------')
#         in_department = kwargs.get('in_department', '')
#         name_check: SearchIndex = cls.objects.filter(name=name).first()
#         if name_check:
#             name_check.return_url = return_url
#             name_check.hash_value = hash_value
#             name_check.in_department = in_department
#             name_check.save()
#             print(name)
#             print(hash_value)
#             print(return_url)
#             print('-------------')
#             return
#         hash_check: SearchIndex = cls.objects.filter(hash_value=hash_value).first()
#         if hash_check:
#             hash_check.return_url = return_url
#             hash_check.name = name
#             hash_check.in_department = in_department
#             hash_check.save()
#             print(name)
#             print(hash_value)
#             print(return_url)
#             print('-------------')
#             return
#         cls.objects.create(
#             name=name,
#             return_url=return_url,
#             in_department=in_department,
#             hash_value=hash_value
#             )
#         print(name)
#         print(hash_value)
#         print(return_url)
#         print('-------------')
#         return

