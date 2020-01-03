
from django.core.management.base import BaseCommand
from config.models import UserTypeStatic

retailer_tag = 'Increase your web exposure, immediately'
retailer_short = ''' Flooring, furniture, appliances, materials - if you sell construction materials or home goods, we can help '''
retailer_full = '''BlueSift allows retailers to list their store and it's products within minutes.
Listed products, and their prices (optionally), are then immediately visible to all users.
No need to worry about entering all the pesky details like a products size, weight or image - we've got that covered.
All you need to do is decide how much you want your business to grow.'''


user_tag = ''' Build. More. Easily '''
user_short = ''' Homeowners, developers, brick and mortar business owners - if you have construction projects, we can help '''
user_full = ''' BlueSift was designed for users. It lets you find exactly the right products and the retailers who carry them.
You no long have to spend days physically searching local retailers, waste time sorting through multiple confusing websites,
or gamble on installing an unseen ecommerce product in your long standing project.
Instead it's all in one place - including the pros that can help you bring your project to life. '''


pro_tag = ''' Get more clients. Streamline project management '''
pro_short = ''' Architects, contractors, designers - if your business helps construction projects come to life, we can help '''
pro_full = ''' Once you join BlueSift, your company becomes visible to every user.
Users - including other pros - can add you to their projects and vice versa.
Shared project schedules allow you to easily assign materials and users to project tasks.
More efficiency + more clients = growth'''

class Command(BaseCommand):
    def handle(self, *args, **options):
        UserTypeStatic.objects.get_or_create(
            label='retailer',
            short_description=retailer_short,
            full_text=retailer_full,
            tagline=retailer_tag
            )
        UserTypeStatic.objects.get_or_create(
            label='user',
            short_description=user_short,
            full_text=user_full,
            tagline=user_tag
            )
        UserTypeStatic.objects.get_or_create(
            label='pro',
            short_description=pro_short,
            full_text=pro_full,
            tagline=pro_tag
            )
        UserTypeStatic.objects.get_or_create(
            label='manufacturer'
            )
