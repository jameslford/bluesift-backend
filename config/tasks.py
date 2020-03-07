"""
celery tasks - these are all asynchronous that exist for this project
"""
from __future__ import absolute_import, unicode_literals
from django.utils import timezone
from celery.utils.log import get_task_logger
from rest_framework.authtoken.models import Token
from BSadmin.models import DangerLog
from config.celery import app



logger = get_task_logger(__name__)


@app.task
def verify_token(token, path, ip_address):
    token = token.replace('Token', '').strip()
    token_obj = Token.objects.filter(key=token).first()
    if token_obj:
        user = token_obj.user
        user.last_seen = timezone.now()
    else:
        message = 'unathorized access attempt from faulty token'
        DangerLog.objects.create(
            ip_address=ip_address,
            message=message,
            base_path=path,
            )


# @app.task
# def harvest_anonymous(session_id, path, params, headers, ip_address):
#     location = headers.get('HTTP_LOCATION')
#     coords = get_location(location)
#     ViewRecord.objects.create(
#         ip_address=ip_address,
#         session_id=session_id,
#         base_path=path,
#         path_params=params,
#         location=coords
#         )


# @app.task
# def harvest_user(token, path, params, headers, ip_address):
#     header_token = headers.get('HTTP_AUTHORIZATION', None)
#     user: User = None
#     if header_token:
#         token = header_token.replace('Token', '').strip()
#         token_obj = Token.objects.filter(key=token).first()
#         if token_obj:
#             user = token_obj.user
#             user.last_seen = timezone.now()
#         else:
#             message = 'unathorized access attempt from faulty token'
#             DangerLog.objects.create(
#                 ip_address=ip_address,
#                 user=user,
#                 message=message,
#                 base_path=path,
#                 path_params=params,
#                 )
#     location = headers.get('HTTP_LOCATION')
#     coords = get_location(location)
#     ViewRecord.objects.create(
#         ip_address=ip_address,
#         user=user,
#         base_path=path,
#         path_params=params,
#         location=coords
#         )






# @app.task
# def harvest_request(headers: Dict, path, ip_address=None):
#     time_threshold = datetime.datetime.now() - datetime.timedelta(hours=10)
#     session_id = headers.get('HTTP_SESSIONID')
#     print(session_id)
#     if session_id:
#         record = ViewRecord.objects.filter(session_id=session_id, recorded__gt=time_threshold).first()
#         if not record:
#             record = ViewRecord.object.create(session_id=session_id)
#     # else 
#     header_token = headers.get('HTTP_AUTHORIZATION', None)
#     user: User = None
#     if header_token:
#         token = header_token.replace('Token', '').strip()
#         token_obj = Token.objects.filter(key=token).first()
#         if token_obj:
#             user = token_obj.user
#             user.last_seen = timezone.now()
#             user.save()
#             record.user = user
#     if user and not user.profile:
#         BaseProfile.objects.create_profile(user)
#         return
#     location = headers.get('HTTP_LOCATION')
#     if location:
#         if user and not user.profile.latest_location:
#             add_location(user, location)
#     record.ip_address = ip_address
#     record.path = path
#     record.save()

    # if user and not user.profile.latest_location:
                # if zipcode and user:
                #     if not user.profile.current_zipcode:
                #         user.profile.current_zipcode = zipcode
                #         user.profile.save()
                #     if not user.profile.latest_location:
                #         user.profile.latest_location = coord
                #         user.profile.save()

# @shared_task
# def check_cache():
#     dirty_qis = QueryIndex.objects.filter(dirty=True)
#     dirty_count = dirty_qis.count()
#     cleaned = 0
#     for index in dirty_qis:
#         if QueryIndex.objects.filter(pk=index.pk).exists():
#             index.refresh()
#             cleaned += 1
#     return f'dirty={dirty_count}, cleaned={cleaned}'


# @shared_task
# def backup_db_task():
#     backup_db()
#     return 'backup complete'


# @shared_task
# def clean_backups_task():
#     clean_backups()
#     return 'backups_cleaned'


# @app.task
# def add_supplier_record(path, pk):
#     record: ViewRecord = ViewRecord.objects.filter(path=path).latest('recorded')
#     retailer = SupplierLocation.objects.filter(pk=pk).first()
#     if record and retailer:
#         if not record.supplier_pk:
#             record.supplier_pk = pk
#             record.save()
