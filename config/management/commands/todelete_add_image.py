# import os
# import urllib
# from django.core.files import File
# from Products.models import Image


# def add_image(location_path, original_location):
#     image = None
#     env = os.environ['DJANGO_SETTINGS_MODULE']
#     if env == 'config.settings.local':
#         image = add_image_local(location_path, original_location)
#     else:
#         image = add_image_web(location_path, original_location)
#     return image


# def add_image_local(location_path, original_location):
#     # print('adding local')
#     new_image = Image.objects.get_or_create(original_url=original_location)[0]
#     read_image = location_path.strip('"')
#     try:
#         with open(read_image, 'rb') as f:
#             image_name = f.name.split('/')[-1]
#             new_image.image.save(image_name, f)
#             new_image.save()
#             f.close()
#             return new_image
#     except FileNotFoundError:
#         return


# def add_image_web(location_path, original_location):
#     try:
#         new_image = Image.objects.get_or_create(original_url=original_location)[0]
#         image_name = location_path.replace('https://', '')
#         image_name = image_name.replace('/', '_')
#         im = urllib.request.urlretrieve(location_path)
#         im = File(open(im[0], 'rb'))
#         new_image.image.save(image_name, im)
#         new_image.save()
#         return new_image
#     except:
#         return
