from django.core.management.base import BaseCommand
from config.scripts.db_operations import revised_to_default, rename
from config.scripts.create_filters import create_finish_surface
from config.scripts.add_zips import add_zips
from config.scripts.assign_size import assign_size
from config.scripts.colors import assign_label_color
from config.scripts.create_usertypes import create_usertypes
from config.scripts.mock_create import create_demo_users
from config.scripts.mock_create_additional import add_additonal
from config.models import LibraryLink


class Command(BaseCommand):
    def handle(self, *args, **options):
        # revised_to_default()
        # rename()
        # add_zips()
        # assign_size()
        # assign_label_color()
        # create_finish_surface()
        # create_usertypes()
        # create_demo_users()
        add_additonal()
        LibraryLink.create_links()
