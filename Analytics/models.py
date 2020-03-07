from django.db import models
from django.conf import settings
from django.http import HttpRequest
from django.contrib.gis.db.models.functions import Distance
from Addresses.models import Coordinate, Zipcode
from .tasks import create_record


class Record(models.Model):
    recorded = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        on_delete=models.SET_NULL,
        )

    ip_address = models.CharField(max_length=200, null=True)
    session_id = models.CharField(max_length=120, null=True)
    base_path = models.CharField(max_length=200, null=True)
    path_params = models.CharField(max_length=300, null=True)
    location = models.ForeignKey(
        Coordinate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
        )

    class Meta:
        abstract = True

    def get_zip(self):
        zipcode = Zipcode.objects.select_related('centroid').annotate(
            distance=Distance('centroid__point', self.location.point)
            ).order_by('distance').first()
        return zipcode


    def parse_request(self, request: HttpRequest, **kwargs):
        model_name = self.__class__.__name__
        redict = request.record_dict
        redict.update({
            'base_path': request.path,
            'user': request.user.pk if request.user and request.user.is_authenticated else None,
            'session_id': request.session.session_key,
            'path_params': request.GET
            })
        redict.update(kwargs)
        create_record.delay(model_name, **redict)


class GenericRecord(Record):
    view = models.CharField(max_length=60)


class ProductDetailRecord(Record):
    product = models.ForeignKey(
        'Products.Product',
        on_delete=models.CASCADE
        )

    def __str__(self):
        return self.product.name

class SupplierProductListRecord(Record):
    supplier = models.ForeignKey(
        'Suppliers.SupplierLocation',
        on_delete=models.CASCADE,
        )

        # location = redict.get('location')

        # self.user = request.user if request.user.isauthenticated else None
        # self.location = get_location(location)
        # self.session_id = request.session.session_key
        # self.path_params = request.GET
        # self.base_path = request.path
        # self.ip_address = redict.get('ip_address')
        # for attr, value in kwargs.items():
        #     setattr(self, attr, value)
        # self.save()
