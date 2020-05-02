# from django.core.management.base import BaseCommand
# from config.models import LibraryLink, ConfigTree
# from scripts.scrapers import create_scrapers, scrape
# from scripts.addresses import add_zips

# # from scripts.products import get_final_images
# from scripts.specialized_products import convert_geometries
# from scripts.finish_surfaces import assign_size, assign_label_color

# # from scripts.facets import create_facets
# from scripts.config import create_usertypes

# # from scripts.demo_data import create_demo_users, add_additonal


# class Command(BaseCommand):
#     def handle(self, *args, **options):
# create_scrapers()
# scrape()
# get_final_images()
# assign_size()
# assign_label_color()
# convert_geometries()
# add_zips()
# create_facets()
# create_usertypes()
# LibraryLink.create_links()
# delete_fake()
# create_demo_users()
# add_additonal()


# def delete_fake():
#     user_model = get_user_model()
#     fake_comps = (
#         SupplierEmployeeProfile.objects.filter(user__demo=True)
#         .values_list("company__pk", flat=True)
#         .distinct()
#     )
#     for comp in fake_comps:
#         company = SupplierCompany.objects.get(pk=comp)
#         company.delete()
#     demos = user_model.objects.filter(demo=True)
#     demos.delete()
