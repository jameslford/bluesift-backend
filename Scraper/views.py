import os
from rest_framework.decorators import (
    api_view,
    permission_classes
    )
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from Scraper.models import ScraperSubgroup, ScraperBaseProduct, ScraperDepartment
from Scraper.ScraperCleaner.models import ScraperCleaner, CleanerUtility
from config.permissions import StagingAdminOnly, StagingorLocalAdmin


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def subgroup_list(request):
    default_subgroups = ScraperSubgroup.objects.using('scraper_default').select_related('category', 'manufacturer').all()

    content = {
        'default_product_count': ScraperBaseProduct.objects.using('scraper_default').count(),
        'revised_product_count': ScraperBaseProduct.objects.count(),
        'groups': []
    }

    for group in default_subgroups:
        category_name = group.category.name
        manufacturer_name = group.manufacturer.name
        revised_group: ScraperSubgroup = ScraperSubgroup.objects.filter(
            category__name=category_name,
            manufacturer__name=manufacturer_name
            ).first()
        group_dict = {
            'name': group.__str__(),
            'revised_pk': revised_group.pk,
            'scraped': group.scraped,
            'cleaned': revised_group.cleaned if revised_group else 'no group',
            'default_count': group.products.count(),
            'revised_count': revised_group.products.count() if revised_group else 'no group'
        }
        content['groups'].append(group_dict)
    return Response(content)

@api_view(['GET'])
@permission_classes((IsAdminUser,))
def subgroup_detail(request, pk):
    revised_subgroup: ScraperSubgroup = ScraperSubgroup.objects.filter(pk=pk).first()

    manufacturer_name = revised_subgroup.manufacturer.name
    category_name = revised_subgroup.category.name
    default_subgroup = ScraperSubgroup.objects.using('scraper_default').filter(
        manufacturer__name=manufacturer_name,
        category__name=category_name
        ).first()

    if not revised_subgroup:
        return Response('invalid pk')
    group_dict = {
        'subgroup': revised_subgroup.__str__(),
        'revised_pk': pk,
        'category_name': revised_subgroup.category.name,
        'commands': CleanerUtility.get_functions_list(),
        'manufacturer_name': revised_subgroup.manufacturer.name,
        'cleaned': revised_subgroup.cleaned,
        'fields': []
        }
    revised_product = ScraperBaseProduct.objects.filter(
        subgroup=revised_subgroup
        ).select_subclasses().first()
    model_type = type(revised_product)
    variable_fields = revised_product.variable_fields()
    default_products = model_type.objects.using('scraper_default').filter(
        subgroup=default_subgroup
        )
    revised_products = model_type.objects.using('scraper_revised').filter(
        subgroup=revised_subgroup
        )
    for field in variable_fields:
        field_dict = {
            'field_name': field,
            'default_values': default_products.values_list(field, flat=True).distinct(),
            'revised_values': revised_products.values_list(field, flat=True).distinct()
            }
        group_dict['fields'].append(field_dict)
    return Response(group_dict)


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def view_products(request, pk):
    """ used to view all products of subgroup from scraper_default that have xxxx value for xxxx field

    Arguments:
        request including 1 parameter
            default_subgroup_pk
        and 2 query parameters:
            field
            value

    Returns:
        list of products
    """
    field = request.GET.get('field', None)
    value = request.GET.get('value', None)
    if not field and value:
        return Response('not enought fields')
    default_subgroup: ScraperSubgroup = ScraperSubgroup.objects.using('scraper_default').filter(pk=pk).first()
    if not default_subgroup:
        return Response('could not find subgroup')
    argument = {field: value, 'subgroup': default_subgroup}
    model = default_subgroup.get_prod_type()
    products = model.objects.using('scraper_default').filter(**argument).values()
    return Response({'products': list(products)})


@api_view(['POST'])
@permission_classes((StagingorLocalAdmin,))
def update_field(request):
    subgroup_pk = request.POST.get('subgroup_pk', None)
    field = request.POST.get('field', None)
    current_value = request.POST.get('current_value', None)
    new_value = request.POST.get('new_value', None)
    if not (subgroup_pk and field and current_value and new_value):
        return Response('not enough fields')
    if new_value == current_value:
        return Response('no difference in new and old value')
    revised_subgroup: ScraperSubgroup = ScraperSubgroup.objects.filter(pk=subgroup_pk).first()
    argument = {field: current_value, 'subgroup': subgroup_pk}
    model_type = revised_subgroup.get_prod_type()
    revised_products = model_type.objects.filter(**argument)
    pks = [product.pk for product in revised_products.all()]
    for product in revised_products:
        setattr(product, field, new_value)
        product.save()
    default_products = model_type.objects.using('scraper_default').filter(pk__in=pks)
    initial_values = default_products.values_list(field, flat=True).distinct()
    for initial_value in initial_values:
        cleaner: ScraperCleaner = ScraperCleaner.objects.get_or_create(
            subgroup_manufacturer_name=revised_subgroup.manufacturer.name,
            subgroup_category_name=revised_subgroup.category.name,
            field_name=field,
            initial_value=initial_value
            )[0]
        cleaner.new_value = new_value
        cleaner.save()
    return Response(status=status.HTTP_201_CREATED)


@api_view(['PUT'])
@permission_classes((StagingorLocalAdmin,))
def alter_values(request):
    revised_subgroup_pk = request.POST.get('subgroup_pk', None)
    value = request.POST.get('value', None)
    if not (value or revised_subgroup_pk):
        return Response('must send revised_subgroup_pk')
    field = request.POST.get('field', None)
    command = request.POST.get('command', None)
    if not field and command:
        return Response('must have field and command')
    revised_subgroup = ScraperSubgroup.objects.using('scraper_revised').filter(pk=revised_subgroup_pk).first()
    products = ScraperBaseProduct.objects.filter(subgroup=revised_subgroup).select_subclasses()
    if value:
        arg = {field: value}
        products = products.filter(**arg)
    for product in products:
        initial_value = getattr(product, field)
        cleaner = CleanerUtility(initial_value)
        new_value = cleaner(command)
        cleaner.create_scraper_cleaner(product.pk, field, new_value)
        setattr(product, field, new_value)
        product.save()
    return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes((StagingorLocalAdmin,))
def stock_clean(request):
    subgroup_pk = request.POST.get('subgroup_pk')
    subgroup: ScraperSubgroup = ScraperSubgroup.objects.get(pk=subgroup_pk)
    subgroup.run_stock_clean()
    return Response(status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def get_departments(request):
    departments = ScraperDepartment.objects.using('scraper_default').all()
    content = {'departments': [{'name': d.name, 'pk': d.pk} for d in departments]}
    return Response(content, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes((StagingorLocalAdmin,))
def department_detail(request, pk):
    # revised_department = ScraperDepartment.objects.get(pk=pk)
    default_department: ScraperDepartment = ScraperDepartment.objects.using('scraper_default').get(pk=pk)
    corresponding_class = default_department.get_product_type()
    variable_fields = corresponding_class.variable_fields()
    content = {'fields': []}
    for field in variable_fields:
        value = {
            'field_name': field,
            'revised_values': list(corresponding_class.objects.values_list(field, flat=True).distinct()),
            'default_values': list(corresponding_class.objects.using('scraper_default').values_list(field, flat=True).distinct())
        }
        content['fields'].append(value)
    return Response(content, status=status.HTTP_200_OK)
