import os
import datetime
from django.conf import settings
from django.db import transaction
from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    @transaction.atomic
    def handle(self, *args, **options):
        now = datetime.datetime.now()
        environment = settings.ENVIRONMENT
        dt_string = now.strftime('%Y-%m-%d')
        env_path = f'data/{environment}/'
        if not os.path.exists(env_path):
            os.makedirs(env_path)
        filename = f'{env_path}backup_{dt_string}.json'
        with open(filename, 'w') as f:
            call_command('dumpdata', indent=2, exclude=[
                'contenttypes',
                'auth',
                'admin',
                'authtoken',
                'django_celery_results',
                'django_celery_beat',
                'ProductFilter.queryindex',
                'ProductFilter.FacetOthersCollection',
                'sessions',
                'Accounts',
                'Suppliers',
                'Projects',
                'Analytics',
                'Profiles',
                'Cards',
                'Orders',
                'Addresses'
                ], stdout=f)
