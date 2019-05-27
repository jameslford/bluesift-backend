from __future__ import absolute_import, unicode_literals
from celery import shared_task
from config.scripts.db_operations import backup_db, clean_backups


@shared_task
def check_cache():
    from ProductFilter.models import QueryIndex
    dirty_qis = QueryIndex.objects.filter(dirty=True)
    for index in dirty_qis:
        if QueryIndex.objects.filter(pk=index.pk).exists():
            index.refresh()


@shared_task
def backup_db_task():
    backup_db()


@shared_task
def clean_backups_task():
    clean_backups()
