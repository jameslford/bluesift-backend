"""
celery tasks - these are all asynchronous that exist for this project
"""
from __future__ import absolute_import, unicode_literals
import logging
import googlemaps
from django.contrib.auth import get_user_model
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_text, force_bytes
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode
from celery import shared_task
from celery.utils.log import get_task_logger
from config.scripts.db_operations import backup_db, clean_backups, scrape, scraper_to_revised, initialize_data, run_stock_clean
from config.scripts.images import get_images
from config.celery import app


logger = get_task_logger(__name__)


@app.task
def add_facet_others_delay(qi_pk, facet_name, intersection_pks):
    from ProductFilter.models import FacetOthersCollection, QueryIndex
    query_index = QueryIndex.objects.filter(pk=qi_pk).first()
    if not query_index:
        return f'No QueryIndex for {query_index}'
    facet: FacetOthersCollection = FacetOthersCollection.objects.get_or_create(
        query_index=query_index,
        facet_name=facet_name
        )
    facet.assign_new_products(intersection_pks)
    return f'FacetOthersCollection created for facet: {facet_name}, and QueryIndex: {qi_pk}'




@app.task
def send_verification_email(site_domain, user_pk):
    user_model = get_user_model()
    try:
        user = user_model.objects.get(pk=user_pk)
        message = render_to_string('acc_activate_email.html', {
            'user': user,
            'domain': site_domain,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': user.auth_token
        })

        email_obj = EmailMessage(
            subject="Activate your Buildbook account",
            body=message,
            from_email='jford@bluesift.com',
            to=[user.email]
            )
        email_obj.send()
        return f'{user.email} email sent'
    except user_model.DoesNotExist:
        logging.warning("Tried to send verification email to non-existent user: '%s'" % user_pk)
        return f'{user.email} email failed'


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
