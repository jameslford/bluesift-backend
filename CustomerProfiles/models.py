# from django.db import models
# from django.conf import settings
# from django.core.exceptions import ValidationError
# from django.contrib.contenttypes.models import ContentType
# from model_utils import Choices
# from config.scripts.globals import valid_subclasses
# from Addresses.models import Address
# from Products.models import Product, ProductSubClass
# from Plans.models import CustomerPlan



# class CustomerProjectApplication(models.Model):
#     # choice_tuple = [cls.__name__ for cls in ProductSubClass.__subclasses__()]
#     # category_choices = Choices((cls.__name__ for cls in ProductSubClass.__subclasses__()))
#     category_choices = valid_subclasses() + ['other']
#     label = models.CharField(max_length=100, blank=True, null=True)
#     project = models.ForeignKey(CustomerProject, on_delete=models.CASCADE, blank=True, related_name='applications')
#     product = models.ForeignKey(CustomerProduct, blank=True, null=True, on_delete=models.SET_NULL)
#     quantity = models.IntegerField()
#     category = Choices(category_choices)
#     start_date = models.DateTimeField(null=True, blank=True)
#     end_date = models.DateTimeField(null=True, blank=True)
#     # category = models.ForeignKey(
#     #     ContentType,
#     #     null=True,
#     #     blank=True,
#     #     on_delete=models.SET_NULL
#     #     )

#     class Meta:
#         unique_together = ('label', 'project')

#     def __str__(self):
#         return self.label

#     def unit(self):
#         pass

#     def get_product_model(self):
#         pass


#     def check_product(self):
#         # pylint: disable=no-member
#         if self.product in self.project.customer_products:
#             return
#         raise Exception('Product not in customer project')

#     # def check_content_type(self):
#     #     valid_subs = valid_subclasses() + ['other']
#     #     if self.category.

#     # def category_selections(self):
#     #     from Products.models import ProductSubClass
#     #     choices = [cls.__name__ for cls in ProductSubClass.__subclasses__()] + ['other']
#     #     return tuple(choices)

