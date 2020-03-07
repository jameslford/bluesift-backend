
from __future__ import absolute_import, unicode_literals
import json
from celery.utils.log import get_task_logger
from config.celery import app
from django.contrib.auth import get_user_model
from Addresses.models import Coordinate
from Suppliers.models import SupplierLocation
from Products.models import Product


logger = get_task_logger(__name__)


def get_location(location):
    if location:
        location = json.loads(location)
        lat = location.get('lat')
        lon = location.get('lon')
        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
                coord = Coordinate.objects.get_or_create(lng=lon, lat=lat)[0]
                return coord
            except (ValueError, AttributeError):
                return None
    return None


@app.task
def create_record(model_name, **kwargs):
    from .models import Record
    for model in Record.__subclasses__():
        if model.__name__ == model_name:
            location = kwargs.get('location')
            location = get_location(location)
            kwargs['location'] = location

            user = kwargs.get('user')
            if user:
                kwargs['user'] = get_user_model().objects.get(pk=user)
            else:
                del kwargs['user']

            if 'supplier' in kwargs:
                supplier = kwargs.pop('supplier')
                kwargs['supplier'] = SupplierLocation.objects.get(pk=supplier)
            
            if 'product' in kwargs:
                product = kwargs.pop('product')
                kwargs['product'] = Product.objects.get(pk=product)

            model.objects.create(**kwargs)