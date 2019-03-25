from Products.models import Product, Manufacturer
from .add_image import add_image


def add_product(row, update):
    bbsku = row['bbsku']
    name = row['name']
    image_original = row['image_original']
    image_local = row['image_local']
    image_final = row['image_final']
    image2_original = row['image2_original']
    image2_local = row['image2_local']
    image2_final = row['image2_final']
    tiling_image = row['tiling_image']
    tiling_image_local = row['tiling_image_local']
    tiling_image_final = row['tiling_image_final']
    manufacturer_name = row['manufacturer_name']
    manufacturer_url = row['manufacturer_url']
    manufacturer_collection = row['manufacturer_collection']
    manufacturer_color = row['manufacturer_color']
    manufacturer_sku = row['manufacturer_sku']
    commercial = row['commercial']
    residential_warranty = row['residential_warranty']
    commercial_warranty = row['commercial_warranty']
    light_commercial_warranty = row['light_commercial_warranty']

    if commercial and commercial is not True and commercial is not False:
        commercial = True if 'rue' in commercial else False

    manufacturer = Manufacturer.objects.get_or_create(label=manufacturer_name)[0]

    product = Product.objects.filter(bb_sku=bbsku).first()
    if product and not update:
        return
    if not product:
        product = Product(bb_sku=bbsku)
    product.manufacturer = manufacturer
    product.manufacturer_url = manufacturer_url
    product.manufacturer_sku = manufacturer_sku
    product.manu_collection = manufacturer_collection
    product.manufacturer_style = manufacturer_color
    product.name = name
    product.commercial = commercial
    product.residential_warranty = residential_warranty
    product.commercial_warranty = commercial_warranty
    product.light_commercial_warranty = light_commercial_warranty

    if not image_local:
        return
    si_image = add_image(image_local, image_original)
    if not si_image:
        return
    product.swatch_image = si_image
    if image2_original:
        rs_image = add_image(image2_local, image2_original)
        if rs_image:
            product.room_scene = rs_image
    if tiling_image:
        ti_image = add_image(tiling_image_local, tiling_image)
        if ti_image:
            product.tiling_image = ti_image

    # product.save()
    return product
