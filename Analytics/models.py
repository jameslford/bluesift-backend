from typing import List
from django.db import models
from Profiles.models import ConsumerProfile
from Groups.models import ProCompany, RetailerCompany
from ProductFilter.models import QueryIndex
from Addresses.models import Coordinate

        # labeled_result = LabeledResult([consumers, retailer_companies, pro_companies], label='plans')
        # graph = GraphResponse([labeled_result], ['consumers', 'retailers', 'pros'])

class LabeledResult:
    def __init__(
            self,
            data: List[int],
            label: str,
            display_type: str = None
        ):
        self.data = data
        self.label = label
        self.display_type = display_type

    def to_dict(self):
        res = {'data': self.data, 'label': self.label}
        if self.display_type:
            res['type'] = self.display_type
        return res


class GraphResponse:
    def __init__(
            self,
            results: List[LabeledResult],
            labels: List[str]
        ):
        self.results = results
        self.labels = labels

    def to_dict(self):
        return {
            'labels': self.labels,
            'results': [res.to_dict() for res in self.results]
        }

class Record(models.Model):
    recorded = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class PlansRecord(Record):

    consumer_plans = models.IntegerField(default=0)
    retailer_plans = models.IntegerField(default=0)
    pro_plans = models.IntegerField(default=0)

    no_plan_consumers = models.IntegerField(default=0)
    no_plan_retailers = models.IntegerField(default=0)
    no_plan_pros = models.IntegerField(default=0)

    def assign_values(self):
        self.consumer_plans = ConsumerProfile.objects.filter(plan__isnull=False).count()
        self.retailer_plans = RetailerCompany.objects.filter(plan__isnull=False).count()
        self.pro_plans = ProCompany.objects.filter(plan__isnull=False).count()

        all_consumers = ConsumerProfile.objects.all().count()
        all_retailer_companies = RetailerCompany.objects.all().count()
        all_pro_companies = ProCompany.objects.all().count()

        self.no_plan_consumers = all_consumers - self.consumer_plans
        self.no_plan_retailers = all_retailer_companies - self.retailer_plans
        self.no_plan_pros = all_pro_companies - self.pro_plans

    def save(self, *args, **kwargs):
        self.assign_values()
        super(PlansRecord, self).save(*args, **kwargs)

    @classmethod
    def get_values(cls):
        consumer_data = []
        retailer_data = []
        pro_data = []
        np_con_data = []
        np_ret_data = []
        np_pro_data = []
        labels = []
        all_values = cls.objects.all()
        for value in all_values:
            consumer_data.append(value.consumer_plans)
            retailer_data.append(value.retailer_plans)
            pro_data.append(value.pro_plans)
            np_con_data.append(value.no_plan_consumers)
            np_ret_data.append(value.no_plan_retailers)
            np_pro_data.append(value.no_plan_pros)
            labels.append(value.recorded)
        return {
            'labels': labels,
            'results': [
                {'data': consumer_data, 'label': 'consumers'},
                {'data': retailer_data, 'label': 'retailers'},
                {'data': pro_data, 'label': 'pros'},
                # {'data': np_con_data, 'label': 'consumers without plan'},
                # {'data': np_ret_data, 'label': 'retailers without plan'},
                # {'data': np_pro_data, 'label': 'pros without plan'},
                ]
            }



class ProductViewRecord(Record):
    user_type = models.CharField(max_length=100)
    ip_address = models.CharField(max_length=200, null=True)
    floating_fields = models.CharField(max_length=200, null=True)
    query_index = models.ForeignKey(
        QueryIndex,
        on_delete=models.SET_NULL,
        null=True,
        related_name='record'
        )
    location = models.ForeignKey(
        Coordinate,
        null=True,
        on_delete=models.SET_NULL,
    )


class CompanyInfoViewRecord(Record):
    pass




class RetailerLocationRecord():
    pass

class DepartmentQueryRecord():
    pass

# class PlansRecord():
#     pass

# class PlansRecord():
#     pass

# class PlansRecord():
#     pass
