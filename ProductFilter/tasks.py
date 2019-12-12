from django.contrib.auth import get_user_model
from config.celery import app
from ProductFilter.models import QueryIndex, FacetOthersCollection
# from Analytics.models import ProductViewRecord, PlansRecord
from Addresses.models import Coordinate


@app.task
def add_facet_others_delay(qi_pk, facet_name, intersection_pks):
    print('in celery qi_pk = ', str(qi_pk))
    query_index = QueryIndex.objects.filter(pk=qi_pk).first()
    if not query_index:
        return f'No QueryIndex for {qi_pk}'
    facet: FacetOthersCollection = FacetOthersCollection.objects.get_or_create(
        query_index=query_index,
        facet_name=facet_name
        )[0]
    facet.assign_new_products(intersection_pks)
    return f'FacetOthersCollection created for facet: {facet_name}, and QueryIndex: {qi_pk}'


# @app.task
# def create_product_view_record(
#         qi_pk,
#         user_pk: str = None,
#         ip_address: str = None,
#         floating_fields: dict = None,
#         lat=None,
#         lng=None
#         ):
#     user_type = 'anon'
#     if user_pk:
#         user = get_user_model().objects.get(pk=user_pk)
#         if user.admin:
#             return
#         if user.is_pro:
#             user_type = 'pro'
#         if user.is_supplier:
#             user_type = 'retailer'
#         else:
#             user_type = 'consumer'
#     pv_record = ProductViewRecord()
#     pv_record.query_index = QueryIndex.objects.get(pk=qi_pk)
#     pv_record.user_type = user_type
#     pv_record.ip_address = ip_address
#     pv_record.floating_fields = floating_fields
#     if lat and lng:
#         coord = Coordinate.objects.get_or_create(
#             lat=lat,
#             lng=lng
#         )
#         pv_record.location = coord
#     pv_record.save()
#     return 'ProductViewRecord Created'
