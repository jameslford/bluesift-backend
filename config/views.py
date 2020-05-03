from django.http.request import HttpRequest
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from Profiles.models import LibraryProduct
from Suppliers.models import SupplierProduct
from .models import UserTypeStatic, ConfigTree, UserFeature
from .serializers import LinkSerializer, ShortLib, ProductStatus


@api_view(["GET"])
def pl_status_for_product(request, pk):
    blah = ProductStatus(request.user, pk)
    return Response(blah.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_short_lib(request, pk=None):
    short_lib = ShortLib(request.user, pk)
    return Response(short_lib.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def user_config(request: HttpRequest):
    user = request.user if request.user and request.user.is_authenticated else None
    conf_tree: ConfigTree = ConfigTree.load()
    res_dict = {
        "profile": user.serialize() if user else None,
        "links": LinkSerializer(user).serialized,
        "departments": conf_tree.product_tree,
        "suppliers": conf_tree.supplier_tree,
    }
    return Response(res_dict)


@api_view(["POST"])
@permission_classes((IsAuthenticated,))
def generic_add(request, collection_pk=None):
    product_pk = request.POST.get("product_pk", None)
    if not product_pk:
        return Response("invalid pk", status=status.HTTP_400_BAD_REQUEST)
    if request.user.is_supplier:
        SupplierProduct.objects.add_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_201_CREATED)
    LibraryProduct.objects.add_product(request.user, product_pk)
    return Response(status=status.HTTP_201_CREATED)


@api_view(["DELETE"])
@permission_classes((IsAuthenticated,))
def generic_delete(request, product_pk, collection_pk=None):
    if request.user.is_supplier:
        SupplierProduct.objects.delete_product(request.user, product_pk, collection_pk)
        return Response(status=status.HTTP_200_OK)
    LibraryProduct.objects.delete_product(request.user, product_pk)
    return Response(status=status.HTTP_200_OK)


@api_view(["GET"])
def landing(request):
    uts = UserTypeStatic.objects.all()
    return Response([ut.serialize() for ut in uts])


@api_view(["GET"])
def ut_features(request, user_type: str):
    if user_type == "user":
        features = UserFeature.objects.filter(supplier=False)
    else:
        features = UserFeature.objects.filter(supplier=True)
    res = [
        {
            "tag_line": feature.label,
            "description": feature.description,
            "img": feature.image,
        }
        for feature in features
    ]
    return Response(res, status=status.HTTP_200_OK)
