import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from config.scripts.db_operations import load_from_backup
from Scraper.models import ScraperSubgroup

class Command(BaseCommand):

    def handle(self, *args, **options):
        username = input('Username:')
        password = getpass.getpass()
        user = get_user_model().objects.filter(email=username).first()
        if not user:
            print('no user')
            return
        confirmed = check_password(password, user.password)
        if not confirmed:
            print('not confirmed')
            return
        if not user.is_admin:
            print('not admin')
            return
        revised_count = ScraperSubgroup.objects.all().count()
        default_count = ScraperSubgroup.objects.using('scraper_default').all().count()
        if revised_count > 0 or default_count > 0:
            self.stdout.write('Data already in database. Will need to flush')
            return
        load_from_backup()