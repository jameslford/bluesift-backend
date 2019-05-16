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
    subgroup: ScraperSubgroup = ScraperSubgroup.objects.filter(pk=pk).first()

    if not subgroup:
        return Response('invalid pk')
    group_dict = {
        'subgroup': subgroup.__str__(),
        'revised_pk': pk,
        'category_name': subgroup.category.name,
        'manufacturer_name': subgroup.manufacturer.name,
        'cleaned': subgroup.cleaned,
        'fields': []
        }
    products = ScraperBaseProduct.objects.filter(subgroup=subgroup).select_subclasses()
    product = products.first()
    if not product:
        group_dict['fields'].append('no products in sub group')
        return Response(group_dict)
    variable_fields = product.variable_fields()
    model_type = type(product)
    for field in variable_fields:
        field_dict = {
            'field_name': field,
            'default_values': model_type.objects.using('scraper_default').values_list(field, flat=True).distinct(),
            'revised_values': model_type.objects.using('scraper_revised').values_list(field, flat=True).distinct()
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
    initial_value = request.GET.get('old_value', None)
    new_value = request.GET.get('new_value', None)
    if not (
            manufacturer and
            category and
            field and
            initial_value and
            new_value):
        return Response('not enough fields')
    if new_value == initial_value:
        return Response('no difference in new and old value')
    default_subgroup = ScraperSubgroup.objects.using('scraper_default').filter(
        manufacturer__name=manufacturer,
        category__name=category
        ).first()
    if not default_subgroup:
        return Response('could not find subgroup')
    argument = {field: initial_value}
    default_products = default_subgroup.products.filter(**argument)
    pks = [product.pk for product in default_products.all()]
    if not pks:
        return Response('no products for this subgroup')
    revised_products = ScraperBaseProduct.objects.using('scraper_revised').filter(pk__in=pks).select_subclasses()
    for product in revised_products:
        setattr(product, field, new_value)
        product.save()
    cleaner: ScraperCleaner = ScraperCleaner.objects.get_or_create(
        subgroup_manufacturer_name=manufacturer,
        subgroup_category_name=category,
        field_name=field,
        initial_value=initial_value
        )[0]
    cleaner.new_value = new_value
    cleaner.product_pks = [product.pk for product in revised_products]
    cleaner.save()
    return Response(status=status.HTTP_201_CREATED)
