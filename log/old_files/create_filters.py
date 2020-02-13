# from ProductFilter.models import ProductFilter
# from django.contrib.contenttypes.models import ContentType
# from SpecializedProducts.models import (
#     FinishSurface,
#     Appliance,
#     Cabinets,
#     # Furniture,
#     # Lumber
#     )

# def create_finish_surface():
#     finish_surface = ContentType.objects.get_for_model(FinishSurface)
#     if not finish_surface:
#         print('no finish surface')
#     fs_filter: ProductFilter = ProductFilter.objects.get_or_create(sub_product=finish_surface)[0]
#     fs_filter.bool_groups = [
#         {
#             "name": "applications",
#             "values": [
#                 "walls",
#                 "countertops",
#                 "floors",
#                 "cabinet_fronts",
#                 "shower_floors",
#                 "shower_walls",
#                 "exterior_walls",
#                 "exterior_floors",
#                 "covered_walls",
#                 "covered_floors",
#                 "pool_linings",
#                 "bullnose",
#                 "covebase",
#                 "corner_covebase"
#                 ]}
#                 ]
#     fs_filter.key_field = 'material'
#     fs_filter.color_field = 'label_color'
#     fs_filter.dependent_fields = [
#         'sub_material',
#         'finish',
#         'surface_coating'
#         ]
#     fs_filter.independent_multichoice_fields = [
#         'look',
#         'shade_variation'
#         ]
#     fs_filter.independent_range_fields = [
#         'size'
#         ]
#     indexes = fs_filter.query_indexes.all()
#     for indice in indexes:
#         others = indice.others.all()
#         others.delete()
#         indice.delete()
#     fs_filter.save()


# def create_appliance():
#     appliance = ContentType.objects.get_for_model(Appliance)
#     if not appliance:
#         print('no appliance')
#         return
#     fs_filter: ProductFilter = ProductFilter.objects.get_or_create(sub_product=appliance)[0]
#     fs_filter.independent_range_fields = [
#         'width',
#         'depth',
#         'height'
#         ]
#     fs_filter.key_field = 'category'
#     indexes = fs_filter.query_indexes.all()
#     for indice in indexes:
#         others = indice.others.all()
#         others.delete()
#         indice.delete()

