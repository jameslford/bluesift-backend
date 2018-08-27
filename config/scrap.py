#     if categories_list:
#         active_cats = _products.values_list('build__category__id', flat=True)
#         for cat in categories:
#             if cat in active_cats:
#                 pass
#             else:
#                 new = products.filter(build__category=cat)
#                 _products = _products | new
#     return _products   

    
# def cat_iteration(orignal_products, products, item, class_name, arg_name):
#     activate_categories = set(products.values_list('build__category__id', flat=True))
#     item_cat = class_name.objects.get(id=item).category
#     search = {arg_name:item}
#     if item_cat.id  in activate_categories:
#         exempt = products.exclude(build__category=item_cat)
#         shaving = orignal_products.filter(**search)
#         return exempt | shaving
#     else:
#         new = orignal_products.filter(**search)
#         return new

    # _products = products
    # if categories_list:
    #     hit = True
    #     _products = products.filter(build__category=categories_list[0])
    #     for cat in categories_list[1:]:
    #         _products = _products | products.filter(build__category=cat)
    # if builds_list:
    #     if hit == True:
    #         for build in builds_list:
    #             if _products.filter(build=build):


    #     else:
    #         pass
    # if materials_list:
    #     if hit == True:
    #         pass
    #     else:
    #         pass




    # if builds[0]:
    #     b_first = {build[1]: build[0][0]}
    #     _products = products.filter(**b_first)
    #     for b in build[0][1:]:
    #         search = {build[1]: b}
    #         _products = _products | products.filter(**search)
    #     if materials[0]:
    #         for mat in materials[0]:
    #             m_search = {materials[1]:mat}
    #             _products = _products | products.filter(**m_search)
    #     if 

        

    # return _products





# def check_categories(products, categories, materials, builds):

#     cats = [cat for cat in categories]

#     for build in builds[0]:
#             build_object = Build.objects.get(id=build)
#             cats.append(build_object.category.id)

#     for mat in materials[0]:
#             material_object = Material.objects.get(id=mat)
#             cats.append(material_object.category.id)

#     cat_set = set(cats)
#     cat_list = list(cat_set)
#     set_count = len(cat_set)

#     if set_count == 0:
#         return products
#     else:
#         _products = products.objects.filter(build__category=cat_list[0])
#         for cat in cat_list[1:]:
#             _products = _products | product.objects.filter(build__category=cat)
#         if builds[0]:
#             _products = filter_builds(_products)




# def filter_builds(products, builds, categories='cats'):
#     _products = products
#     term = builds[1]
#     build_list = builds[0]
#     if build_list:
#         _products
#     else:
#         return products

# def filter_categories(products, categories):
#     _products = products
#     if categories[0]:
#         _products = _products.filter(build__category=categories[0])
#         for cat in categories[1:]:
#             _products = _products | product.filter(build__category=cat)
#         return _products
#     else:
#         return _products








# def check_list(products, arg_list):
#     _products = products
#     full_args = [arg for arg in arg_list if arg[0]]
#     if full_args:
#         first_search = {full_args[0][1]:full_args[0][0]}
#         _products = _products.filter(**first_search)
#         for args in full_args[1:]:
#             for arg in args[0]:
#                 next_search = {args[1]:arg}
#                 _products = _products | products.filter()



    # for args in arg_list:
    #     if args[0]:
    #         term = args[1]
    #         first_search = {term: args[0][0]}
    #         _products = products.filter(**first_search)
    #         for arg in arg_list[0][1:]:
    #             second_search = {arg_list[1]:arg}
    #             results = results | _products.filter(**second_search)
    #         return results







  

#     # filter products
#     pTyped_products = parse_pt(product_type)
#     aTyped_products = parse_at(application_type, pTyped_products)
#     for_sale_products = parse_for_sale(for_sale, aTyped_products)
#     filtered_products = parse_manufacturer(manufacturer, for_sale_products)
#     sorted_products = sort_products(sort, filtered_products)
#     products_serialized = ProductSerializer(sorted_products, many=True)
 

#     # filter application types
#     application_types = Application.objects.all()
#     refined_ats = type_refiner(
#                                 ApplicationAreaSerializer, 
#                                 application_types, 
#                                 filtered_products, 
#                                 'application'
#                                 )

#     # filter manufacturers
#     manufacturers = Manufacturer.objects.all()
#     refined_manu = type_refiner(
#                                 ManufacturerSerializer, 
#                                 manufacturers, 
#                                 for_sale_products, 
#                                 'manufacturer'
#                                 )

#     # filter product types
#     product_types = ProductType.objects.all()
#     refined_pts = type_refiner(
#                                 ProductTypeSerializer, 
#                                 product_types, 
#                                 filtered_products, 
#                                 'product'
#                                 )

#     filter_content = {
#         "for_sale" : for_sale,
#         "product_count" : filtered_products.count()
#     } 

#     return Response({
#                     "filter" : [filter_content],
#                     "application_types": refined_ats,
#                     "product_types": refined_pts,
#                     "manufacturers": refined_manu,
#                     "products": products_serialized.data
#                     })
    
# def sort_products(sort, products):
#     if sort == 'none':
#         return products
#     else:
#         try:
#            sorted_products = products.order_by('sort')
#            return sorted_products
#         except:
#             return products



# def parse_pt(product_type):
#     products = Product.objects.all()
#     if product_type == '0':
#         return products
#     else:
#         return products.filter(product_type=product_type)

# def parse_at(application_type, products):
#     if application_type == ['0']:
#         return products
#     else:
#         for at in application_type:
#             products = products.filter(application=at)
#         return products

# def parse_manufacturer(manufacturer, products):
#     if manufacturer == '0':
#         return products
#     else:
#         return products.filter(manufacturer=manufacturer)


# def parse_for_sale(for_sale, products):
#     if for_sale == 'true':   
#         return products.filter(for_sale=True)
#     else:
#         return products


# def type_refiner(serializer, objects, products, argument):
#     serialized_types = []
#     for item in objects:
#         count = get_argument(item, products, argument)
#         at_serialized = serializer(item).data
#         at_serialized['count'] = count
#         if count > 0:
#             at_serialized['enabled'] = True
#         serialized_types.append(at_serialized)
#     return serialized_types

# def get_argument(item, products, argument):
#     if argument == 'application':
#         return products.filter(application=item).count()
#     elif argument == 'product':
#         return products.filter(product_type=item).count()
#     elif argument == 'manufacturer':
#         return products.filter(manufacturer=item).count()

# def product_sort(products, argument):
#     pass

