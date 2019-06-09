from __future__ import absolute_import, unicode_literals
from celery import shared_task
from celery.utils.log import get_task_logger
from config.scripts.db_operations import backup_db, clean_backups, scrape, scraper_to_revised, initialize_data, run_stock_clean
from config.scripts.images import get_images

logger = get_task_logger(__name__)

@shared_task
def check_cache():
    from ProductFilter.models import QueryIndex
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


@shared_task
def subgroup_command(command):
    if command == 'scrape_new':
        initialize_data()
        scrape()
        get_images()
        scraper_to_revised()
    elif command == 'clean_new':
        run_stock_clean()
    else:
        return 'bad command called'
    return f'{command} run'
