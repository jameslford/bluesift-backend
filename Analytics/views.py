"""
Analytics.views
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from config.custom_permissions import SupplierAdminPro
from Suppliers.models import SupplierLocation


@api_view(["GET"])
@permission_classes((SupplierAdminPro,))
def supplier_view_records(request):
    group = request.user.get_group()
    locations = SupplierLocation.objects.select_related("address").filter(company=group)
    views_array = []
    views = {}
    keys = []
    for loc in locations:
        loc: SupplierLocation = loc
        loc_name = loc.nickname
        loc_key = {"name": loc_name, "pk": loc.pk}
        keys.append(loc_key)
        for date in loc.view_record_list():
            date_string = str(date["date"])
            exists = views.get(date_string)
            if exists:
                views[date_string][loc_name] = date["count"]
            else:
                views[date_string] = {loc_name: date["count"]}
    for key, stores in views.items():
        new_dict = {"date": key}
        total = 0
        for store, count in stores.items():
            total += count
            new_dict[store] = count
            new_dict["total"] = total
        views_array.append(new_dict)
    return Response({"views": views_array, "keys": keys}, status=status.HTTP_200_OK)
