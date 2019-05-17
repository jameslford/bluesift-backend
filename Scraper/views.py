import os
from rest_framework.decorators import (
    api_view,
    permission_classes
    )
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from Scraper.models import ScraperSubgroup, ScraperBaseProduct
from Scraper.ScraperCleaner.models import ScraperCleaner
from .permissions import StagingAdminOnly, StagingorLocalAdmin


@api_view(['GET'])
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
    default_subgroup = ScraperSubgroup.objects.using('scraper_default').filter(pk=pk).first()
    if not default_subgroup:
        return Response('could not find subgroup')
    argument = {field: value}
    products = default_subgroup.products.filter(**argument).values()
    return Response(list(products))


@api_view(['POST'])
@permission_classes((StagingorLocalAdmin,))
def update_revised(request):
    manufacturer = request.POST.get('manufacturer', None)
    category = request.POST.get('category', None)
    field = request.GET.get('field', None)
    current_value = request.GET.get('current_value', None)
    new_value = request.GET.get('new_value', None)
    if not (
            manufacturer and
            category and
            field and
            current_value and
            new_value):
        return Response('not enough fields')
    if new_value == current_value:
        return Response('no difference in new and old value')
    revised_subgroup = ScraperSubgroup.objects.using('scraper_revised').filter(
        manufacturer__name=manufacturer,
        category__name=category
        ).first()
    if not revised_subgroup:
        return Response('could not find subgroup')
    argument = {field: current_value}
    revised_products = revised_subgroup.products.filter(**argument)
    pks = [product.pk for product in revised_products.all()]
    if not pks:
        return Response('no products for this subgroup')
    for product in revised_products:
        setattr(product, field, new_value)
        product.save()
    default_products = ScraperBaseProduct.objects.using('scraper_default').filter(pk__in=pks).select_subclasses()
    initial_values = default_products.values_list(field, flat=True).distinct()
    cleaner: ScraperCleaner = ScraperCleaner.objects.get_or_create(
        subgroup_manufacturer_name=manufacturer,
        subgroup_category_name=category,
        field_name=field,
        new_value=new_value
        )[0]
    cleaner.initial_values = initial_values
    cleaner.default_product_pks = [product.pk for product in default_products]
    cleaner.save()
    return Response(status=status.HTTP_201_CREATED)
