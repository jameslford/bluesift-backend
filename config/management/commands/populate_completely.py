from django.core.management.base import BaseCommand
from config.models import LibraryLink
from scripts.scrapers import create_scrapers, scrape
from scripts.addresses import add_zips
from scripts.products import get_final_images
from scripts.specialized_products import convert_geometries
from scripts.finish_surfaces import assign_size, assign_label_color
from scripts.facets import create_facets
from scripts.config import refresh_product_tree, create_usertypes
from scripts.demo_data import create_demo_users, add_additonal

class Command(BaseCommand):

    def handle(self, *args, **options):
        create_scrapers()
        scrape()
        get_final_images()
        assign_size()
        assign_label_color()
        convert_geometries()
        add_zips()
        create_facets()
        refresh_product_tree()
        create_usertypes()
        create_demo_users()
        add_additonal()
        LibraryLink.create_links()
