# Products.views.py

from django.shortcuts import render
from django.core.serializers import serialize
from django.db.models import Q

from rest_framework.generics import RetrieveAPIView
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import(
                        ProductSerializer, 
                        ManufacturerSerializer
                        )

from .models import(
                    Product, 
                    Build,
                    Material, 
                    Manufacturer,
                    Category 
                    )



@api_view(['GET'])
def product_list(request):

    products = Product.objects.all()

    # ______parse request________

    # product lists
    manufacturers   = [request.GET.getlist('manufacturers'), 'manufacturer']
    builds          = [request.GET.getlist('build'), 'build__id']
    materials       = [request.GET.getlist('material'), 'material']
    look            = [request.GET.getlist('look'), 'look']
    
    # method lists
    categories      = [request.GET.getlist('categories'), 'build__category']


    for_sale        = [request.GET.get('for_sale'), 'for_sale']
    floors          = [request.GET.get('floors'), 'floors']
    walls           = [request.GET.get('walls'), 'walls']
    countertops     = [request.GET.get('countertops'), 'countertops']
    exterior        = [request.GET.get('exterior'), 'exterior']
    covered         = [request.GET.get('covered'), 'covered']
    shower_floors   = [request.GET.get('showerFloor'), 'shower_floors']
    shower_walls    = [request.GET.get('showerWall'), 'shower_walls']
    pool_linings    = [request.GET.get('pool_lining'), 'pool_linings']

    # specialty values
    cof = request.GET.get('cof')
    lrv = request.GET.get('lrv')
    color = request.GET.get('color')

    # sort
    sort = request.GET.get('sort', 'none')

    # arguments
    product_boolean_args = [for_sale, floors, walls, countertops, exterior, covered, shower_floors, shower_walls, pool_linings]
    count = len(categories[0]) + len(builds[0]) + len(materials[0])

    # ____filter_____
    products = check_booleans(products, product_boolean_args)

    if count == 1:
        if builds[0]:
            products = subtract_else(products, builds)
        if materials[0]:
            products = subtract_else(products, materials)
        if categories[0]:
            products = subtract_else(products, categories)


    elif count > 1:
        products = parse_BMC(products, materials, categories, builds)
    
    manufacturer_values = products.values('manufacturer__id', 'manufacturer__name').distinct()
    filter_manufacturer = []
    for manu in manufacturer_values:
        count = products.filter(manufacturer__id=manu['manufacturer__id']).count()
        manu['count'] = count
        manu['enabled'] = False
        if manu['manufacturer__id'] in manufacturer_values:
            manu['enabled'] = True
        filter_manufacturer.append(manu)

    if manufacturers[0]:
        products = or_list_query(products, manufacturers)

    all_cats = Category.objects.all().values('label', 'id')
    filter_cats = products.values_list('build__category__id', flat=True).distinct()
    filter_builds = products.values_list('build__id', flat=True).distinct()
    filter_mats = products.values_list('material__id', flat=True).distinct()


    for cat in all_cats:
        cat['enabled'] = False
        cat['builds'] = []
        cat['materials'] = []
        if cat['id'] in filter_cats:
            cat['enabled'] = True
        cat_builds = Build.objects.filter(category__id=cat['id'])
        cat_mats = Material.objects.filter(category__id=cat['id'])
        for cb in cat_builds:
            listing = {'label': cb.label, 'id': cb.id, 'enabled': False}
            if cb.id in filter_builds:
                listing['enabled'] = True
                cat['builds'].append(listing)
            else:
                cat['builds'].append(listing)
        for mat in cat_mats:
            listing = {'label': mat.label, 'id': mat.id, 'enabled': False}
            if mat.id in filter_mats:
                listing['enabled'] = True
                cat['materials'].append(listing)
            else:
                cat['materials'].append(listing)


    product_count = products.count()

    filter_response = {
        'manufacturers' : filter_manufacturer,
        'all_cats': all_cats,
        'filter_bools': bool_response(products, product_boolean_args)
    }

    return Response({
        'for_sale': for_sale[0],
        'product_count': product_count,
        'filter': filter_response,
        'products': ProductSerializer(products, many=True).data
        })

def bool_response(products, args):
    bool_filter = []
    for arg in args:
        content = {'label': arg[1], 'count': 0, 'enabled': False}
        search = {arg[1]:True}
        count = products.filter(**search).count()
        content['count'] = count
        if arg[0] == 'True':
            content['enabled'] = True
            bool_filter.append(content)
        else:
            bool_filter.append(content)
    return bool_filter






def parse_BMC(products, materials, categories, builds):
    materials_list = materials[0]
    build_list = builds[0]
    categories_list = categories[0]
    _products = products
    hit = False
    if build_list:
        hit = True
        _products = products.filter(build=build_list[0])
        for build in build_list[1:]:
            _products = _products | products.filter(build=build)
    if materials_list and hit == False:
        hit = True
        _products = products.filter(material=materials_list[0])
        for material in materials_list[1:]:
            _products = _products | products.filter(material=material)
    elif materials_list and hit == True:
        for material in materials_list:
            active_cats = set(_products.values_list('build__category__id', flat=True))
            material_category = Material.objects.get(id=material).category.id
            if material_category in active_cats:
                exempt = _products.exclude(build__category=material_category)
                active = _products.filter(material=material)
                _products = exempt | active
            else:
                _products = _products | products.filter(material=material)
        for category in categories_list[1:]:
            _products = _product | products.filter(build__category=category)
    elif categories_list and hit == True:
        for category in categories:
            exempt = _products.exclude(build__category=category)
            new = products.filter(build__category=category)
            _products = exempt | new
    return _products


def subtract_else(products, args):
    search = {args[1]:args[0][0]}
    return products.filter(**search)


def check_booleans(products, arg_list):
    _products = products
    for arg in arg_list:
        if arg[0]:
            search = {arg[1]:arg[0]}
            _products = _products.filter(**search)
    return _products




def or_list_query(products, arg_list):
    _products = products
    search_list = arg_list[0]
    term = arg_list[1]
    if search_list:
        first_search = {term: search_list[0]}
        _products = products.filter(**first_search)
        for item in search_list[1:]:
            next_search = {term: item}
            _products = _products | products.filter(**next_search)
        return _products
    else:
        return _products


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



@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.get(id=pk)
    serialized_product = ProductSerializer(product)
    return Response({'product': serialized_product.data})


