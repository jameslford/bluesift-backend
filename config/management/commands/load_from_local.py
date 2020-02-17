
import os
import glob
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):

    def handle(self, *args, **options):
        environment = settings.ENVIRONMENT
        if environment == 'staging':
            path = 'data/local/*.json'
            backups = glob.glob(path)
            latest = max(backups, key=os.path.getctime)
            call_command('loaddata', latest)
