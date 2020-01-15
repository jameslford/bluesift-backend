from django.db import models
from django.conf import settings
from Addresses.models import Coordinate


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
    best_location = models.BooleanField(default=False)

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

