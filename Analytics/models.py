from django.db import models
from django.conf import settings
from Addresses.models import Coordinate
# from typing import List
# from pandas import date_range as pdate_range
# from datetime import date, timedelta, datetime
# from django.db.models import Min, Max, Count, QuerySet
# from django.db.models.functions import TruncWeek, TruncDay, TruncMonth
# from Profiles.models import ConsumerProfile
# from Groups.models import ProCompany, RetailerCompany
# from UserProductCollections.models import RetailerLocation
# from ProductFilter.models import QueryIndex


class Record(models.Model):
    recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class ViewRecord(Record):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        related_name='viewRecords'
        )
    ip_address = models.CharField(max_length=200, null=True)
    session_id = models.CharField(max_length=120, null=True)
    path = models.CharField(max_length=500, null=True)
    base_path = models.CharField(max_length=200, null=True)
    path_params = models.CharField(max_length=300, null=True)
    cleaned = models.BooleanField(default=False)
    product_detail_pk = models.CharField(max_length=120, null=True)
    supplier_pk = models.IntegerField(null=True)
    pro_company_pk = models.IntegerField(null=True)
    location = models.ForeignKey(
        Coordinate,
        null=True,
        on_delete=models.SET_NULL
        )

    def split_path(self):
        if '?' in self.path:
            self.base_path, self.path_params = self.path.split('?')

    def check_location(self):
        pass
        # if self.location:
        #     return

# class PlansRecord(Record):

#     consumer_plans = models.IntegerField(default=0)
#     retailer_plans = models.IntegerField(default=0)
#     pro_plans = models.IntegerField(default=0)

#     no_plan_consumers = models.IntegerField(default=0)
#     no_plan_retailers = models.IntegerField(default=0)
#     no_plan_pros = models.IntegerField(default=0)

#     def assign_values(self):
#         self.consumer_plans = ConsumerProfile.objects.filter(plan__isnull=False).count()
#         self.retailer_plans = RetailerCompany.objects.filter(plan__isnull=False).count()
#         self.pro_plans = ProCompany.objects.filter(plan__isnull=False).count()

#         all_consumers = ConsumerProfile.objects.all().count()
#         all_retailer_companies = RetailerCompany.objects.all().count()
#         all_pro_companies = ProCompany.objects.all().count()

#         self.no_plan_consumers = all_consumers - self.consumer_plans
#         self.no_plan_retailers = all_retailer_companies - self.retailer_plans
#         self.no_plan_pros = all_pro_companies - self.pro_plans

#     def save(self, *args, **kwargs):
#         self.assign_values()
#         super(PlansRecord, self).save(*args, **kwargs)

#     @classmethod
#     def get_values(cls):
#         consumer_data = []
#         retailer_data = []
#         pro_data = []
#         np_con_data = []
#         np_ret_data = []
#         np_pro_data = []
#         labels = []
#         all_values = cls.objects.all()
#         for value in all_values:
#             consumer_data.append(value.consumer_plans)
#             retailer_data.append(value.retailer_plans)
#             pro_data.append(value.pro_plans)
#             np_con_data.append(value.no_plan_consumers)
#             np_ret_data.append(value.no_plan_retailers)
#             np_pro_data.append(value.no_plan_pros)
#             labels.append(value.recorded)
#         return {
#             'labels': labels,
#             'results': [
#                 {'data': consumer_data, 'label': 'consumers'},
#                 {'data': retailer_data, 'label': 'retailers'},
#                 {'data': pro_data, 'label': 'pros'},
#                 ]
#             }


# LOCATION_BIG_ARG = 'query_index__retailer_location__in'
# LOCATION_SMALL_ARG = 'query_index__retailer_location'
# LOCATION_LABEL = 'nickname'
# GROUP_BIG_ARG = 'query_index__retailer_location__company__in'
# GROUP_SMALL_ARG = 'query_index__retailer_location__company'
# GROUP_LABEL = 'name'

# INTERVAL_OTIONS = {
#     'day': [TruncDay, 'D', 'day'],
#     'week': [TruncWeek, 'W', 'week'],
#     'month': [TruncMonth, 'M', 'month']
# }



# class PRQueryMapper:
#     def __init__(self, queryset: QuerySet, interval: str = 'day'):
#         self.queryset: QuerySet = queryset
#         self.interval = interval
#         self.interval_func = None
#         self.int_alias = None
#         self.big_arg = None
#         self.dti_attr = None
#         self.small_arg = None
#         self.label = None
#         self.assign_values()

#     def assign_values(self):
#         self.interval_func, self.int_alias, self.dti_attr = INTERVAL_OTIONS[self.interval]
#         if self.queryset.model is RetailerLocation:
#             self.big_arg = LOCATION_BIG_ARG
#             self.small_arg = LOCATION_SMALL_ARG
#             self.label = LOCATION_LABEL
#         elif self.queryset.model is RetailerCompany:
#             self.big_arg = GROUP_BIG_ARG
#             self.small_arg = GROUP_SMALL_ARG
#             self.label = GROUP_LABEL
#         else:
#             raise ValueError('unsupported queryset type')


# class LabeledResult:
#     def __init__(
#             self,
#             data: List[int],
#             label: str,
#             display_type: str = None
#         ):
#         self.data = data
#         self.label = label
#         self.display_type = display_type

#     def to_dict(self):
#         res = {'data': self.data, 'label': self.label}
#         if self.display_type:
#             res['type'] = self.display_type
#         return res


# class GraphResponse:
#     def __init__(
#             self,
#             results: List[LabeledResult],
#             labels: List[str]
#         ):
#         self.results = results
#         self.labels = labels

#     def to_dict(self):
#         return {
#             'labels': self.labels,
#             'results': [res.to_dict() for res in self.results]
#         }



# class ProductViewRecord(Record):
#     user_type = models.CharField(max_length=100)
#     ip_address = models.CharField(max_length=200, null=True)
#     floating_fields = models.CharField(max_length=200, null=True)
#     created = models.DateTimeField(auto_now_add=True)
#     query_index = models.ForeignKey(
#         QueryIndex,
#         on_delete=models.SET_NULL,
#         null=True,
#         related_name='record'
#         )
#     location = models.ForeignKey(
#         Coordinate,
#         null=True,
#         on_delete=models.SET_NULL,
#     )

#     @classmethod
#     def views_time_series(cls, locations: QuerySet, interval='day'):
#         grargs = PRQueryMapper(locations, interval)
#         records = cls.objects.select_related(
#             'query_index',
#             'query_index__retailer_location'
#         ).filter(**{grargs.big_arg: grargs.queryset})
#         today = datetime.utcnow().date()
#         min_date = records.aggregate(Min('created'))
#         min_date = min_date['created__min']
#         if not min_date:
#             min_date = today - timedelta(30)
#         else:
#             min_date = min_date.date()
#         all_dates = pdate_range(start=min_date, end=today, freq=grargs.int_alias, tz='UTC')
#         labels = [adat for adat in all_dates]
#         results = []
#         for quer in grargs.queryset:
#             recs = records.filter(**{grargs.small_arg: quer}).annotate(
#                 interval=grargs.interval_func('created')
#                 ).values('interval').annotate(count=Count('id')).values('interval', 'count')
#             new_recs = {rec['interval']: rec['count'] for rec in recs}
#             print(new_recs)
#             results.append({
#                 'label': getattr(quer, grargs.label),
#                 'data': [new_recs.get(label, 0) for label in labels]
#                 })
#         return {'labels': labels, 'results': results}


        # location_pks = locations.values_list('pk', flat=True)
        # records = cls.objects.select_related(
        #     'query_index',
        #     'query_index__retailer_location'
        # ).filter(query_index__retailer_location__pk__in=location_pks)
        # min_date = records.aggregate(Min('created'))
        # min_date = min_date['created__min'].date()
        # today = datetime.utcnow().date()
        # labels = pdate_range(start=min_date, end=today, tz='UTC')
        # results = []
        # for location in locations:
        #     recs = records.filter(query_index__retailer_location__pk=location.pk).annotate(
        #         date=TruncDay('created')
        #         ).values('date').annotate(count=Count('id')).values('date', 'count')
        #     new_recs = {rec['date']: rec['count'] for rec in recs}
        #     results.append({
        #         'label': location.nickname,
        #         'data': [new_recs.get(label, 0) for label in labels]
        #         })
        # return {'labels': labels, 'results': results}



# class CompanyInfoViewRecord(Record):
#     pass


# class RetailerLocationRecord():
#     pass


# class DepartmentQueryRecord():
#     pass

# class PlansRecord():
#     pass

# class PlansRecord():
#     pass

# class PlansRecord():
#     pass
