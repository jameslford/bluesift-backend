"""
celery tasks - these are all asynchronous that exist for this project
"""
from __future__ import absolute_import, unicode_literals
# import logging
import datetime
from typing import Dict
from celery import shared_task
from celery.utils.log import get_task_logger
from rest_framework.authtoken.models import Token
from ProductFilter.models import QueryIndex
from Addresses.models import Coordinate
from config.celery import app
from config.scripts.db_operations import (
    backup_db,
    clean_backups,
    scraper_to_revised,
    initialize_data,
    run_stock_clean
    )

logger = get_task_logger(__name__)

@app.task
def harvest_request(headers: Dict, host, path):
    pass
    # header_token = headers.get('HTTP_AUTHORIZATION', None)
    # user = None
    # if header_token:
    #     token = header_token.replace('Token', '').strip()
    #     token_obj = Token.objects.filter(key=token).first()
    #     if token_obj:
    #         user = token_obj.user
    #         user.last_seen = datetime.datetime.now()
    #         user.save()
    # print(headers, host, path)


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


# @shared_task
# def subgroup_command(command):
#     if command == 'scrape_new':
#         initialize_data()
#         scrape()
#         get_images()
#         scraper_to_revised()
#     elif command == 'clean_new':
#         run_stock_clean()
#     else:
#         return 'bad command called'
#     return f'{command} run'
