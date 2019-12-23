import itertools
from django.db import transaction
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes
    )
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from Scraper.models import ScraperSubgroup, ScraperDepartment
from Scraper.ScraperCleaner.models import ScraperCleaner
from config.custom_permissions import StagingorLocalAdmin
from .tasks import subgroup_scrape, subgroup_clean, department_scrape


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def department_list(request):
    default_departments = ScraperDepartment.objects.using('scraper_default').all()
    dep_list = [dep.serialize_list() for dep in default_departments]
    return Response(dep_list, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def department_detail(request, dep: str):
    default_department: ScraperDepartment = ScraperDepartment.objects.using('scraper_default').get(name=dep)
    revised_department: ScraperDepartment = ScraperDepartment.objects.get(name=dep)
    product_type = default_department.get_product_type()
    variable_fields = product_type.variable_fields()
    content = {
        'revised_pk': revised_department.pk,
        'default_pk': default_department.pk,
        'fields': []
        }
    for field in variable_fields:
        value = {
            'field_name': field,
            'revised_values': list(product_type.objects.values_list(field, flat=True).distinct()),
            'default_values': list(product_type.objects.using(
                'scraper_default').values_list(field, flat=True).distinct())
        }
        content['fields'].append(value)
    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((IsAdminUser,))
def subgroup_detail(request, pk):
    subgroup: ScraperSubgroup = ScraperSubgroup.objects.get(pk=pk)
    return Response(subgroup.get_field_values())


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def subgroups_list(request, department: str):
    default_subgroups = ScraperSubgroup.objects.using(
        'scraper_default').select_related('category', 'manufacturer').filter(category__department__name=department)
    revised_subgroups = ScraperSubgroup.objects.select_related(
        'category', 'manufacturer').filter(category__department__name=department)
    groups = []
    for default, revised in itertools.zip_longest(default_subgroups, revised_subgroups):
        first = next((group for group in [default, revised]), None)
        if not first:
            continue
        group_dict = {
            'name': str(first),
            'manufacturer': str(first.manufacturer),
            'category': first.category.name,
            'pk': revised.pk,
            'scraped': default.scraped if default else False,
            'cleaned': revised.cleaned if revised else False,
            'default_count': default.products.count() if default else 'no group',
            'revised_count': revised.products.count() if revised else 'no group'
        }
        groups.append(group_dict)
    return Response(groups)


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def view_products(request, pk):
    field = request.GET.get('field')
    value = request.GET.get('value')
    search_group = request.GET.get('search_group')
    db_ver = request.GET.get('db', 'scraper_default')
    if not (field and value and search_group):
        return Response('not enought fields')
    if search_group == 'subgroup':
        subgroup: ScraperSubgroup = ScraperSubgroup.objects.using(db_ver).get(pk=pk)
        model = subgroup.get_prod_type()
        if value == 'null':
            arg = field + '__isnull'
            argument = {arg: True}
        else:
            argument = {field: value}
        products = subgroup.get_products().filter(**argument)
        return Response([prod.serialize_short() for prod in products])
    if search_group == 'department':
        department: ScraperDepartment = ScraperDepartment.objects.using(db_ver).get(pk=pk)
        model = department.get_product_type()
        if value == 'null':
            arg = field + '__isnull'
            argument = {arg: True, 'subgroup__category__department': department}
        else:
            argument = {field: value, 'subgroup__category__department': department}
        products = model.objects.using(db_ver).filter(**argument)
        return Response([prod.serialize_short() for prod in products])
    return Response('invalid searchgroup', status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes((StagingorLocalAdmin,))
@transaction.atomic()
def update_field(request, pk: int):
    field = request.POST.get('field')
    current_value = request.POST.get('current_value')
    new_value = request.POST.get('new_value')
    group_type = request.POST.get('group_type')

    if not (field and current_value and group_type):
        return Response('not enough fields')
    if new_value == current_value:
        return Response('no difference in new and old value')
    if group_type == 'subgroup':
        revised_subgroup: ScraperSubgroup = ScraperSubgroup.objects.filter(pk=pk).first()
        model_type = revised_subgroup.get_prod_type()
        revised_products = revised_subgroup.get_products().filter(**{field: current_value})
        revised_products.update(**{field: new_value})
    elif group_type == 'department':
        department: ScraperDepartment = ScraperDepartment.objects.get(pk=pk)
        model_type = department.get_product_type()
        revised_products = department.get_product_type().objects.filter(**{field: current_value})
        revised_products.update(**{field: new_value})
    else:
        return Response('invalid group type')
    pks = [product.pk for product in revised_products.all()]
    default_products = model_type.objects.using('scraper_default').filter(pk__in=pks)
    initial_subgroups = default_products.values_list('subgroup__pk', flat=True)
    for sub_pk in initial_subgroups:
        initial_sub = ScraperSubgroup.objects.using('scraper_default').get(pk=sub_pk)
        def_sub_prods = initial_sub.get_products()
        initial_values = def_sub_prods.values_list(field, flat=True).distinct()
        for initial_value in initial_values:
            cleaner: ScraperCleaner = ScraperCleaner.objects.get_or_create(
                subgroup_manufacturer_name=initial_sub.manufacturer.name,
                subgroup_category_name=initial_sub.category.name,
                field_name=field,
                initial_value=initial_value
                )[0]
            cleaner.new_value = new_value
            cleaner.save()
    new_vals = model_type.objects.filter(pk__in=pks)
    for val in new_vals:
        print(val.name)
    return Response(list(new_vals.values_list(field, flat=True)), status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes((StagingorLocalAdmin,))
def clean_subgroup(request):
    subgroup_pk = request.POST.get('pk')
    if not subgroup_pk:
        return Response('no pk')
    subgroup: ScraperSubgroup = ScraperSubgroup.objects.filter(pk=subgroup_pk).first()
    if not subgroup:
        subgroup = ScraperSubgroup.objects.using('scraper_default').filter(pk=subgroup_pk).first()
    if not subgroup:
        return Response('invalid pk')
    res = subgroup_clean.delay(pk=subgroup.pk)
    return Response(res.id)


@api_view(['POST'])
@permission_classes((StagingorLocalAdmin,))
def scrape_subgroup(request):
    subgroup_pk = request.POST.get('subgroup_pk')
    if not subgroup_pk:
        return Response('no pk')
    subgroup = ScraperSubgroup.objects.filter(pk=subgroup_pk).first()
    if not subgroup:
        subgroup = ScraperSubgroup.objects.using('scraper_default').filter(pk=subgroup_pk).first()
    if not subgroup:
        return Response('invalid pk')
    res = subgroup_scrape.delay(subgroup.pk)
    return Response(res.id)


@api_view(['POST'])
@permission_classes((StagingorLocalAdmin,))
def scrape_department(request):
    department_pk = request.POST.get('department_pk')
    if not department_pk:
        return Response('no pk')
    department = ScraperDepartment.objects.filter(pk=department_pk).first()
    if not department:
        department = ScraperDepartment.objects.using('scraper_default').filter(pk=department_pk).first()
    if not department:
        return Response('invalid pk')
    res = department_scrape.delay(department.pk)
    return Response(res.id)


@api_view(['POST'])
@permission_classes((StagingorLocalAdmin,))
def clean_department(request):
    department_pk = request.POST.get('department_pk')
    if not department_pk:
        return Response('no pk')
    department = ScraperDepartment.objects.filter(pk=department_pk).first()
    if not department:
        department = ScraperDepartment.objects.using('scraper_default').filter(pk=department_pk).first()
    if not department:
        return Response('invalid pk')
    res = department_scrape.delay(department.pk)
    return Response(res.id)


    # subgroup_pk = int(subgroup_pk)
    # default_subgroup: ScraperSubgroup = ScraperSubgroup.objects.using('scraper_default').filter(pk=subgroup_pk).first()
    # if not default_subgroup:
    #     revised_subgroup = ScraperSubgroup.objects.get(pk=subgroup_pk)
    #     default_subgroup = revised_subgroup.save(db='default_subgroup')
    # default_subgroup.scrape()

# 'default_pk': default.pk if default else None,
# 'revised_pk': revised.pk if revised else None,

# @api_view(['PUT'])
# @permission_classes((StagingorLocalAdmin,))
# def alter_values(request):
#     revised_subgroup_pk = request.POST.get('subgroup_pk', None)
#     value = request.POST.get('value', None)
#     if not (value or revised_subgroup_pk):
#         return Response('must send revised_subgroup_pk')
#     field = request.POST.get('field', None)
#     command = request.POST.get('command', None)
#     if not field and command:
#         return Response('must have field and command')
#     revised_subgroup = ScraperSubgroup.objects.using('scraper_revised').filter(pk=revised_subgroup_pk).first()
#     products = ScraperBaseProduct.objects.filter(subgroup=revised_subgroup).select_subclasses()
#     if value:
#         arg = {field: value}
#         products = products.filter(**arg)
#     for product in products:
#         initial_value = getattr(product, field)
#         cleaner = CleanerUtility(initial_value)
#         new_value = cleaner(command)
#         cleaner.create_scraper_cleaner(product.pk, field, new_value)
#         setattr(product, field, new_value)
#         product.save()
#     return Response(status=status.HTTP_200_OK)



# @api_view(['PUT'])
# @permission_classes((StagingorLocalAdmin,))
# def stock_clean(request):
#     subgroup_pk = request.POST.get('pk')
#     subgroup: ScraperSubgroup = ScraperSubgroup.objects.get(pk=subgroup_pk)
#     subgroup.run_stock_clean()
#     return Response(status=status.HTTP_200_OK)

# @api_view(['POST'])
# @permission_classes((StagingorLocalAdmin,))
# @transaction.atomic()
# def update_subgroup_property(request: HttpRequest, pk):
#     field = request.POST.get('field', None)
#     subgroup = None
#     if field == 'cleaned':
#         subgroup = ScraperSubgroup.objects.get(pk=pk)
#     elif field == 'scraped':
#         subgroup = ScraperSubgroup.objects.using('scraper_default').get(pk=pk)
#     else:
#         return Response('invalid field', status=status.HTTP_400_BAD_REQUEST)
#     value = not getattr(subgroup, field)
#     setattr(subgroup, field, value)
#     subgroup.save()
#     return Response(status=status.HTTP_200_OK)


# from config.tasks import subgroup_command as task_subgroup_command

# SCRAPE_NEW = 'scrape_new'
# CLEAN_NEW = 'clean_new'

# SUBGROUP_COMMANDS = [
#     SCRAPE_NEW,
#     CLEAN_NEW
# ]

    # revised_subgroup: ScraperSubgroup = ScraperSubgroup.objects.get(pk=pk)
    # manufacturer_name = revised_subgroup.manufacturer.name
    # category_name = revised_subgroup.category.name
    # default_subgroup = ScraperSubgroup.objects.using('scraper_default').filter(
    #     manufacturer__name=manufacturer_name,
    #     category__name=category_name
    #     ).first()

    # if not revised_subgroup:
    #     return Response('invalid pk')
    # group_dict = {
    #     'name': revised_subgroup.__str__(),
    #     'revised_pk': revised_subgroup.pk,
    #     'default_pk': default_subgroup.pk,
    #     'category_name': revised_subgroup.category.name,
    #     'commands': None,
    #     'manufacturer_name': revised_subgroup.manufacturer.name,
    #     'cleaned': revised_subgroup.cleaned,
    #     'fields': []
    #     }
    # revised_product = ScraperBaseProduct.objects.filter(
    #     subgroup=revised_subgroup
    #     ).select_subclasses().first()
    # model_type = type(revised_product)
    # variable_fields = revised_product.variable_fields()
    # default_products = model_type.objects.using('scraper_default').filter(
    #     subgroup=default_subgroup
    #     )
    # revised_products = model_type.objects.using('scraper_revised').filter(
    #     subgroup=revised_subgroup
    #     )
    # for field in variable_fields:
    #     field_dict = {
    #         'field_name': field,
    #         'default_values': default_products.values_list(field, flat=True).distinct(),
    #         'revised_values': revised_products.values_list(field, flat=True).distinct()
    #         }
    #     group_dict['fields'].append(field_dict)


# @api_view(['POST'])
# @permission_classes((StagingorLocalAdmin,))
# @transaction.atomic()
# def run_subgroup_command(request: HttpRequest):
#     command = request.POST.get('command', None)
#     if command not in SUBGROUP_COMMANDS:
#         return Response('invalid command', status=status.HTTP_403_FORBIDDEN)
#     if command == SCRAPE_NEW:
#         task_subgroup_command.delay(SCRAPE_NEW)
#     if command == CLEAN_NEW:
#         task_subgroup_command.delay(CLEAN_NEW)
#     return Response(status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes((StagingorLocalAdmin,))
# def update_subgroup_field(request, subgroup_pk: int):
#     field = request.POST.get('field')
#     current_value = request.POST.get('current_value')
#     new_value = request.POST.get('new_value')

#     if not (field and current_value):
#         return Response('not enough fields')
#     if new_value == current_value:
#         return Response('no difference in new and old value')
#     revised_subgroup: ScraperSubgroup = ScraperSubgroup.objects.filter(pk=subgroup_pk).first()
#     # if not revised_subgroup.cleaned:
#     #     return Response('Should be stock cleaned first', status=status.HTTP_400_BAD_REQUEST)
#     argument = {field: current_value, 'subgroup': subgroup_pk}
#     model_type = revised_subgroup.get_prod_type()
#     revised_products = model_type.objects.filter(**argument)
#     pks = [product.pk for product in revised_products.all()]
#     for product in revised_products:
#         setattr(product, field, new_value)
#         product.save()
#     default_products = model_type.objects.using('scraper_default').filter(pk__in=pks)
#     initial_values = default_products.values_list(field, flat=True).distinct()
#     for initial_value in initial_values:
#         cleaner: ScraperCleaner = ScraperCleaner.objects.get_or_create(
#             subgroup_manufacturer_name=revised_subgroup.manufacturer.name,
#             subgroup_category_name=revised_subgroup.category.name,
#             field_name=field,
#             initial_value=initial_value
#             )[0]
#         cleaner.new_value = new_value
#         cleaner.save()
#     return Response(status=status.HTTP_201_CREATED)


# if not revised_subgroup.cleaned:
#     return Response('Should be stock cleaned first', status=status.HTTP_400_BAD_REQUEST)
# argument = {field: current_value, 'subgroup': pk}
# model_type = revised_subgroup.get_prod_type()
# revised_products = model_type.objects.filter(**argument)

# @api_view(['POST'])
# @permission_classes((StagingorLocalAdmin,))
# @transaction.atomic()
# def update_department_field(request: HttpRequest, department_pk: int):
#     field = request.POST.get('field')
#     # if field not in ('width', 'thickness', 'length'):
#     #     return Response('cannot alter this field', status=status.HTTP_400_BAD_REQUEST)
#     current_value = request.POST.get('current_value')
#     new_value = request.POST.get('new_value')

#     department: ScraperDepartment = ScraperDepartment.objects.get(pk=department_pk)
#     revised_products = department.get_product_type().objects.filter(**{field: current_value})
#     revised_products.update(**{field: new_value})
#     # for revised_product in revised_products:
#     #     setattr(revised_product, field, new_value)
#     default_products = department.get_product_type().objects.using('scraper_default').filter(
#         pk__in=[product.pk for product in revised_products])
#     default_subs = default_products.values_list('subgroup__pk', flat=True).distinct()
#     for sub in default_subs:
#         subgroup = ScraperSubgroup.objects.using('scraper_default').get(pk=sub)
#         initial_values = subgroup.products.values_list(field, flat=True).distinct()
#         for initial_value in initial_values:
#             cleaner: ScraperCleaner = ScraperCleaner.objects.get_or_create(
#                 subgroup_manufacturer_name=subgroup.manufacturer.name,
#                 subgroup_category_name=subgroup.category.name,
#                 field_name=field,
#                 initial_value=initial_value
#                 )[0]
#             cleaner.new_value = new_value
#             cleaner.save()
#     return Response(status=status.HTTP_201_CREATED)