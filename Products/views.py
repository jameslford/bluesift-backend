''' Products.views.py '''
import math
from decimal import Decimal
from django.db.models import Count
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination


from .serializers import(
    ProductSerializer,
    ManufacturerSerializer,
    ProductDetailSerializer
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

    request_url = request.GET.urlencode().split('&')
    request_url = ['&&'+query for query in request_url]
    request_url = [query for query in request_url if 'page' not in query]
    manufacturers = [request.GET.getlist('manufacturer'), 'manufacturer']
    builds = [request.GET.getlist('build__id'), 'build__id']
    materials = [request.GET.getlist('material'), 'material']
    look = [request.GET.getlist('look'), 'look']
    categories = [request.GET.getlist('build__category'), 'build__category']
    for_sale = [request.GET.get('for_sale'), 'for_sale']
    floors = [request.GET.get('floors'), 'floors']
    walls = [request.GET.get('walls'), 'walls']
    countertops = [request.GET.get('countertops'), 'countertops']
    cabinet_fronts = [request.GET.get('cabinet_fronts'), 'cabinet_fronts']
    exterior = [request.GET.get('exterior'), 'exterior']
    covered = [request.GET.get('covered'), 'covered']
    shower_floors = [request.GET.get('shower_floors'), 'shower_floors']
    shower_walls = [request.GET.get('shower_walls'), 'shower_walls']
    pool_linings = [request.GET.get('pool_linings'), 'pool_linings']
    cof = request.GET.get('cof')
    lrv = request.GET.get('lrv')
    finish = request.GET.get('finish')
    thk = request.GET.get('thk')
    color = request.GET.get('color')
    sort = request.GET.get('sort', 'none')
    page = request.GET.get('page', 1)

    products = Product.objects.all()

    if thk:
        thk = Decimal(thk)
        products = products.filter(thickness=thk)

    if finish:
        products = products.filter(finish=finish)
    

    product_boolean_args = [
        for_sale,
        floors,
        walls,
        countertops,
        cabinet_fronts,
        exterior,
        covered,
        shower_floors,
        shower_walls,
        pool_linings
        ]
    
    products = check_booleans(products, product_boolean_args)


    if manufacturers[0]:
        products = or_list_query(products, manufacturers)

    all_cats = filter_BCM(products, categories, builds, materials)

    count = len(categories[0]) + len(builds[0]) + len(materials[0])
    if count == 1:
        if builds[0]:
            products = subtract_else(products, builds)
        if materials[0]:
            products = subtract_else(products, materials)
        if categories[0]:
            products = subtract_else(products, categories)
    elif count > 1:
        products = parse_BMC(products, materials, categories, builds)

    filter_manufacturer = filter_manufacturers(products, manufacturers)    

    product_count = products.count()
    bools = bool_response(products, product_boolean_args)

    paginator = PageNumberPagination()
    paginator.page_size = 16
    products_response = paginator.paginate_queryset(products, request)
    serialized_products = ProductSerializer(products_response, many=True)

    page_count = math.ceil(product_count/paginator.page_size)
    load_more = True
    page = int(page)
    if not page:
        page = 1
    if page == page_count:
        load_more = False

    # thickness = products.values_list('thickness', flat=True).distinct()
    thickness = products.values('thickness').distinct().annotate(count=Count('thickness'))
    finishes = products.values('finish__label', 'id').annotate(count=Count('finish__label'))


    filter_response = {
        'for_sale': bools[0],
        'filter_bools': bools[1:],
        'manufacturers' : filter_manufacturer,
        'thicknesses': thickness,
        'finishes': finishes,
        'all_cats': all_cats
    }

    return Response({
        'product_count': product_count,
        'query' : request_url,
        'load_more': load_more,
        'current_page': page,
        'filter': filter_response,
        'products': serialized_products.data
        })


def filter_BCM(products, categories, builds, materials):
    all_cats = Category.objects.all().values('label', 'id')
    for cat in all_cats:
        cat['enabled'] = False
        cat['count'] = products.filter(build__category=cat['id']).count()
        cat['builds'] = []
        cat['materials'] = []
        if str(cat['id']) in categories[0]:
            cat['enabled'] = True
        cat_builds = Build.objects.filter(category__id=cat['id'])
        cat_mats = Material.objects.filter(category__id=cat['id'])
        for build in cat_builds:
            count = products.filter(build=build).count()
            listing = {'label': build.label, 'id': build.id, 'count': count, 'enabled': False}
            if str(build.id) in builds[0]:
                listing['enabled'] = True
                cat['builds'].append(listing)
            else:
                cat['builds'].append(listing)
        for mat in cat_mats:
            count = products.filter(material=mat).count()
            listing = {'label': mat.label, 'id': mat.id, 'count': count, 'enabled': False}
            if str(mat.id) in materials[0]:
                listing['enabled'] = True
                cat['materials'].append(listing)
            else:
                cat['materials'].append(listing)
    return all_cats


def filter_manufacturers(products, args):
    all_manufacturers = Manufacturer.objects.all()
    filter_manufacturer = []
    for manu in all_manufacturers:
        unit = {}
        count = products.filter(manufacturer=manu).count()
        unit['count'] = count
        unit['id'] = manu.id
        unit['label'] = manu.name
        if str(manu.id) in args[0]:
            unit['enabled'] = True
            filter_manufacturer.append(unit)
        else:
            unit['enabled'] = False
            filter_manufacturer.append(unit)
    return filter_manufacturer


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
    hit = False
    _products = products
    if build_list:
        hit = True
        _products = products.filter(build__id=build_list[0])
        for build in build_list[1:]:
            _products = _products | products.filter(build__id=build)
    if materials_list and hit:
        active_cats = set(_products.values_list('build__category__id', flat=True))
        for mat in materials_list:
            mat_object = Material.objects.get(id=mat)
            if mat_object.category.id in active_cats:
                material_category = mat_object.category
                exempt = _products.exclude(build__category=material_category)
                active = _products.filter(material=mat_object)
                _products = exempt | active
            else:
                _products = _products | products.filter(material=mat_object)
    elif materials_list:
        _products = products.filter(material=materials_list[0])
        for mat in materials_list[1:]:
            _products = _products | products.filter(material__id=mat)
    if categories_list:
        for cat in categories_list:
            _products = _products | products.filter(build__category__id=cat)
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



@api_view(['GET'])
def get_product(request, pk):
    product = Product.objects.get(id=pk)
    serialized_product = ProductDetailSerializer(product)
    return Response({'product': serialized_product.data})
