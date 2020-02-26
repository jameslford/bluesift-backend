from django.db import models


class SearchIndex(models.Model):
    name = models.CharField(max_length=200, unique=True)
    return_url = models.CharField(max_length=200)
    in_department = models.CharField(max_length=150, blank=True, null=True)
    hash_value = models.CharField(max_length=2000, unique=True)


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
            print(name)
            print(hash_value)
            print(return_url)
            print('-------------')
            return
        hash_check: SearchIndex = cls.objects.filter(hash_value=hash_value).first()
        if hash_check:
            hash_check.return_url = return_url
            hash_check.name = name
            hash_check.in_department = in_department
            hash_check.save()
            print(name)
            print(hash_value)
            print(return_url)
            print('-------------')
            return
        cls.objects.create(
            name=name,
            return_url=return_url,
            in_department=in_department,
            hash_value=hash_value
            )
        print(name)
        print(hash_value)
        print(return_url)
        print('-------------')
        return



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

