"""
celery tasks - these are all asynchronous that exist for this project
"""
from __future__ import absolute_import, unicode_literals
import json
from typing import Dict
from django.utils import timezone
from django.contrib.gis.db.models.functions import Distance
from celery import shared_task
from celery.utils.log import get_task_logger
from rest_framework.authtoken.models import Token
from ProductFilter.models import QueryIndex
from Addresses.models import Coordinate, Zipcode
from Analytics.models import ViewRecord
from Suppliers.models import SupplierLocation
from Groups.models import SupplierCompany
from config.celery import app
from scripts.db_operations import (
    backup_db,
    clean_backups,
    )

logger = get_task_logger(__name__)


@app.task
def harvest_request(headers: Dict, path, ip_address=None):
    header_token = headers.get('HTTP_AUTHORIZATION', None)
    user = None
    record = ViewRecord()
    if header_token:
        token = header_token.replace('Token', '').strip()
        token_obj = Token.objects.filter(key=token).first()
        if token_obj:
            user = token_obj.user
            user.last_seen = timezone.now()
            user.save()
            record.user = user
    location = headers.get('HTTP_LOCATION')
    if location:
        location = json.loads(location)
        lat = location.get('lat')
        lon = location.get('lon')
        if lat and lon:
            try:
                lat = float(lat)
                lon = float(lon)
                coord = Coordinate.objects.get_or_create(lat=lat, lng=lon)
                zipcode = Zipcode.objects.select_related('zipcode').annotate(
                    distance=Distance('centroid__point', coord)
                    ).order_by('distance').first()
                if zipcode and user:
                    user.current_zipcode = zipcode
                    user.save()
                record.best_location = True
                record.location = coord
            except (ValueError, AttributeError):
                pass
    session_id = headers.get('HTTP_SESSIONID')
    if session_id:
        record.session_id = session_id
    record.ip_address = ip_address
    record.path = path
    record.save()


@shared_task
def check_cache():
    dirty_qis = QueryIndex.objects.filter(dirty=True)
    dirty_count = dirty_qis.count()
    cleaned = 0
    for index in dirty_qis:
        if QueryIndex.objects.filter(pk=index.pk).exists():
            index.refresh()
            cleaned += 1
    return f'dirty={dirty_count}, cleaned={cleaned}'


@shared_task
def backup_db_task():
    backup_db()
    return 'backup complete'


@shared_task
def clean_backups_task():
    clean_backups()
    return 'backups_cleaned'


@app.task
def add_supplier_record(path, pk):
    record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
    retailer = SupplierLocation.objects.filter(pk=pk).first()
    if record and retailer:
        if not record.supplier_pk:
            record.supplier_pk = pk
            record.save()
