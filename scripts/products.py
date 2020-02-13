import io
from django.conf import settings
from Products.models import Product
from utils.downloads import url_to_pimage
from utils.images import resize_image


def get_final_images(update=False):
    products = Product.objects.all()
    for product in products:
        desired_size = settings.DESIRED_IMAGE_SIZE
        img_groups = [
            [product.swatch_image_original, product.swatch_image],
            [product.room_scene_original, product.room_scene],
            [product.tiling_image_original, product.tiling_image]
        ]
        for img_group in img_groups:
            original = img_group[0]
            destination = img_group[1]
            if not original:
                print('no local')
                continue
            if not update and destination:
                print('already got final')
                continue
            image = url_to_pimage(original)
            image = image.convert('RGB')
            image = resize_image(image, desired_size)
            if not image:
                continue
            buffer = io.BytesIO()
            try:
                image.save(buffer, 'JPEG')
            except IOError:
                print('io error')
                continue
            images_name = str(product.manufacturer_sku) + '.jpg'
            destination.save(images_name, buffer, save=True)
            print('getting final for ' + product.name)






# def validate_image(image: pimage.Image):
#     """ validates pillow image """
#     try:
#         image.verify()
#         return True
#     except:
#         print('image wouldnt verify')
#         return False



    # try:
    #     image.verify()
    #     return image
    # except:
    #     print('image wouldnt verify')
    #     return None
    # image_copy = copy.copy(image)
    # if not validate_image(image_copy):
    #     print('not valid image')
    #     return None
    # return image



        # image.save(buffer, 'PNG', optimize=True)
        # image = product.resize_image(image)
        # if not image:
        #     print('bad image - final')
        #     continue
        # buffer = io.BytesIO()


    # try:
    #     image = pimage.open(image)
    # except (OSError, ValueError) as e:
    #     image = None
    #     product.save()
    #     return None


    # def get_local_images(product, update=False):
#     images = [
#         [product.swatch_image_original, product.swatch_image_local],
#         [product.room_scene_original, product.room_scene_local],
#         [product.tiling_scene_original, product.tiling_scene_local]
#     ]
#     for img_group in images:
#         if not img_group[0]:
#             continue
#         url = img_group[0]
#         destination = img_group[1]
#         if not update and destination:
#             print('already got')
#             continue
#         image_name = f'local_{str(product.manufacturer_sku)}.png'
#         image: pimage.Image = product.download_image(url)
#         if not image:
#             continue
#         buffer = io.BytesIO()
#         image.save(buffer, 'PNG', optimize=True)
#         destination.save(image_name, File(buffer), save=False)
#         print('getting local for ' + product.name)
#         product.save()
