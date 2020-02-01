# import getpass
# from django.core.management.base import BaseCommand
# from django.contrib.auth import get_user_model
# from django.contrib.auth.hashers import check_password
# from ...scripts.db_operations import initialize_data, scrape, scraper_to_revised
# from ...scripts.images import get_images


# class Command(BaseCommand):
#     def handle(self, *args, **options):
#         username = input('Username:')
#         password = getpass.getpass()
#         user = get_user_model().objects.filter(email=username).first()
#         if not user:
#             print('no user')
#             return
#         confirmed = check_password(password, user.password)
#         if not confirmed:
#             print('not confirmed')
#             return
#         if not user.is_admin:
#             print('not admin')
#             return
#         self.stdout.write(self.style.WARNING('This will rescrape all data. Are you sure?'))
#         confirm = input('please answer [yes/no]')
#         if confirm == 'yes':
#             initialize_data()
#             scrape(True)
#             get_images()
#             scraper_to_revised()
