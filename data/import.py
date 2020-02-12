# import os
# import json
# import glob
# import datetime
# from django.core.management import call_command
# from Products.models import Product
# from SpecializedProducts.derivatives.base import ProductSubClass
# # from django.contrib.contenttypes.models import ContentType

# def transfer_data():
#     import_data()
#     export_data()

# def export_data():
#     dt_string = datetime.datetime.now()
#     filename = 'data/out/' + str(dt_string) + '.json'
#     db_args = ['SpecializedProducts.FinishSurfaces', 'SpecializedProducts.Appliances']
#     with open(filename, 'w+') as f:
#         call_command('dumpdata', db_args, stdout=f)

# def import_data():
#     path_in = 'data/*.json'
#     files = glob.glob(path_in)
#     latest = max(files, key=os.path.getctime)
#     with open(latest, 'r') as fin:
#         products = json.load(fin)
#     for product in products:
#         blah = DataImporter(**product)
#         blah.match()


# class DataImporter:

#     def __init__(self, **kwargs):
#         self._kwargs = kwargs
#         self.model_type: ProductSubClass = None

#     def match(self):
#         bb_sku = self._kwargs.get('bb_sku')
#         if bb_sku:
#             product: ProductSubClass = Product.subclasses.get_subclass(pk=bb_sku)
#             product.import_update(self._kwargs)
#             return
#         self.model_type.import_new(self._kwargs)
#         return
        # model = self._kwargs.get('model')
        # if not model:
        #     raise ValueError('no model provided for', self._kwargs)
        # content_type: ContentType = ContentType.objects.get(app_label='SpecializedProducts', model=model)
        # self.model_type = content_type.model_class()

        # terms = {}
        # manufacturer_sku = self._kwargs.get('manufacturer_sku')
        # manufacturer = self._kwargs.get('manufacturer')
        # manufacturer_collection = self._kwargs.get('manufacturer_collection')
        # manufacturer_style = self._kwargs.get('manufacturer_style')
        # if manufacturer_sku:
        #     terms.update('manufacturer_sku', manufacturer_sku)
        # if manufacturer:
        #     terms.update('manufacturer_label', manufacturer)
        # if manufacturer_collection:
        #     terms.update('manufacturer_collection', manufacturer_collection)
        # if manufacturer_style:
        #     terms.update('manufacturer_style', manufacturer_style)
        # products = model.objects.filter(**terms)
        # if not products:
        #     return
        # self.model_type.import_match(product, self._kwargs)
        # return