import datetime
from django.http.request import HttpRequest
from django.core.files.storage import get_storage_class
from django.db.models import Count, CharField, F
from django.db.models.query import Value
from django.db.models.functions import Concat
from rest_framework.request import Request
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from config.globals import check_department_string
from config.custom_permissions import PrivateSupplierCrud
from config.serializers import BusinessSerializer
from Analytics.models import SupplierProductListRecord
from Profiles.models import SupplierEmployeeProfile
from ProductFilter.sorter import FilterResponse
from .models import SupplierLocation, SupplierProduct
from .serializers import (
    serialize_location_public_detail,
    serialize_location_private_detail,
)


@api_view(["GET"])
def public_locations_list_view(request: Request, category=None):
    suppliers = (
        SupplierLocation.objects.select_related(
            "address", "address__postal_code", "address__coordinates",
        )
        .prefetch_related("products",)
        .all()
    )
    if category:
        prod_class = check_department_string(category)
        if prod_class is None:
            return Response("invalid model type", status=status.HTTP_400_BAD_REQUEST)
        supplier_product_pks = prod_class.objects.values(
            "priced__location__pk"
        ).distinct()
        suppliers = suppliers.filter(pk__in=supplier_product_pks)
    res = suppliers.annotate(
        product_count=Count("products"),
        lat=F("address__coordinates__lat"),
        lng=F("address__coordinates__lng"),
        address_string=F("address__address_string"),
    ).values(
        "nickname",
        "pk",
        "product_count",
        "phone_number",
        "email",
        "lat",
        "lng",
        "address_string",
    )
    return Response(res, status=status.HTTP_200_OK)


@api_view(["GET"])
def public_location_detail_view(request: HttpRequest, pk: int):

    model: SupplierLocation = SupplierLocation.objects.select_related(
        "address", "address__postal_code", "address__coordinates", "company"
    ).prefetch_related("products", "products__product").get(pk=pk)

    sdr = SupplierProductListRecord()
    sdr.parse_request(request, supplier=pk)
    info = serialize_location_public_detail(model)
    # info.update({'tree': model.product_tree.get_trees().serialize()})

    return Response(info, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes((PrivateSupplierCrud,))
def private_locations_list(request):
    group = request.user.get_group()
    locations = SupplierLocation.objects.select_related("address").filter(company=group)
    res = [serialize_location_private_detail(loc) for loc in locations]
    # series = [{'date': date, store: count for store, count in res}]
    return Response({"locations": res}, status=status.HTTP_200_OK)


@api_view(["GET", "POST", "DELETE", "PUT"])
@permission_classes((PrivateSupplierCrud,))
def crud_location(request: Request, pk: int = None):
    """
    privaste location view only for employees
    create, update, delete endpoint for SupplierLocation objects
    """
    user = request.user

    if request.method == "GET":
        if not pk:
            return Response("no pk provided", status=status.HTTP_400_BAD_REQUEST)
        location = user.get_collections().get(pk=pk)
        info = BusinessSerializer(location, True).getData()
        info.update({"tree": location.product_tree.get_trees().serialize()})
        return Response(info, status=status.HTTP_200_OK)

    if request.method == "POST":
        data = request.data
        SupplierLocation.objects.create_location(user, **data)
        return Response(status=status.HTTP_201_CREATED)

    if request.method == "PUT":
        data = request.data
        location = SupplierLocation.objects.update_location(user, **data)
        return Response(
            BusinessSerializer(location).getData(), status=status.HTTP_200_OK
        )

    if request.method == "DELETE":
        location = user.get_collections.all().filter(pk=pk).first()
        location.delete()
        return Response(status=status.HTTP_200_OK)

    return Response("unsupported method", status=status.HTTP_405_METHOD_NOT_ALLOWED)


@api_view(["DELETE", "GET", "PUT"])
def crud_supplier_products(request: HttpRequest, product_type=None):

    imageurl = get_storage_class().base_path()

    if request.method == "GET":
        res = FilterResponse.get_cache(request, product_type)
        pks = [prod["pk"] for prod in res["products"]]
        supplier = request.GET.get("supplier_pk")
        location = SupplierLocation.objects.get(pk=supplier)
        products = (
            location.products.select_related("product", "product__manufacturer")
            .filter(product__pk__in=pks)
            .annotate(
                swatch_url=Concat(
                    Value(imageurl), "product__swatch_image", output_field=CharField()
                ),
            )
        )

        res["products"] = products.values(
            "pk",
            "in_store_ppu",
            "online_ppu",
            "units_available_in_store",
            "units_per_order",
            "lead_time_ts",
            "offer_installation",
            "publish_in_store_availability",
            "publish_in_store_price",
            "publish_online_price",
            "swatch_url",
            "product__pk",
            "product__unit",
            "product__manufacturer_style",
            "product__manufacturer_collection",
            "product__manufacturer_sku",
            "product__manufacturer__label",
        )
        return Response(res, status=status.HTTP_200_OK)

    if request.method == "PUT":
        data = request.data
        profile: SupplierEmployeeProfile = request.user.get_profile()
        location = data.get("location_pk")
        location: SupplierLocation = request.user.get_collections().get(pk=location)
        if not (profile == location.local_admin or profile.owner or profile.admin):
            return Response("unauthorized", status=status.HTTP_401_UNAUTHORIZED)
        changes = data.get("changes")
        updates = 0
        for change in changes:
            product_pk = change.get("pk")
            product: SupplierProduct = location.products.filter(pk=product_pk).first()
            if not product:
                continue
            in_store_ppu = data.get("in_store_ppu")
            units_available_in_store = data.get("units_available_in_store")
            lead_time_ts = data.get("lead_time_ts")
            lead_time_ts = datetime.timedelta(days=lead_time_ts)
            product.update(
                in_store_ppu=in_store_ppu,
                units_available_in_store=units_available_in_store,
                lead_time_ts=lead_time_ts,
            )
            updates += 1
        return Response(f"{updates} products updated", status=status.HTTP_200_OK)

    return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


def supplier_product(request, pk: int):
    product = SupplierProduct.objects.get(pk=pk)
    return Response(product.serialize_mini, status=status.HTTP_200_OK)
