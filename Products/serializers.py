from typing import Dict
from .models import Product
from SpecializedProducts.models import ProductSubClass


def serialize_detail_quick(product: ProductSubClass):
    stock = serialize_stock(product)
    special = product.grouped_fields()
    special.update({"warranty": serialize_warranty(product)})
    priced = [price.serialize_mini() for price in product.get_in_store_priced()]
    stock.update(
        {
            "manufacturer_url": product.manufacturer_url,
            "room_scene": product.room_scene.url if product.room_scene else None,
            "priced": priced,
            "lists": special,
        }
    )
    return stock


def serialize_detail(product: ProductSubClass):
    stock = serialize_stock(product)
    special = product.grouped_fields()
    special.update({"warranty": serialize_warranty(product)})
    priced = [price.serialize_mini() for price in product.get_in_store_priced()]
    parents = [product._meta.verbose_name_plural] + [
        parent._meta.verbose_name_plural for parent in product._meta.get_parent_list()
    ]
    stock.update(
        {
            "parents": parents[::-1],
            "manufacturer_url": product.manufacturer_url,
            "room_scene": product.room_scene.url if product.room_scene else None,
            "priced": priced,
            "geometry": product.presentation_geometries(),
            "lists": special,
        }
    )
    return stock


def serialize_product(product: Product) -> Dict[str, any]:
    return {
        "pk": product.pk,
        "unit": product.unit,
        "hash_value": product.hash_value,
        "category": product.category,
        "width": product.derived_width,
        "height": product.derived_height,
        "depth": product.derived_depth,
        "manufacturer_style": product.manufacturer_style,
        "manufacturer_collection": product.manufacturer_collection,
        "manufacturer_sku": product.manufacturer_sku,
        "name": product.name,
        "swatch_url": product.swatch_image.url if product.swatch_image else None,
        "manufacturer__label": product.manufacturer.label,
        "low_price": getattr(product, "low_price", None),
    }


def serialize_product_priced(product: Product) -> Dict[str, any]:
    prod_dict = serialize_product(product)
    prod_dict["suppliers"] = [prod.get_priced() for prod in product.priced.all()]
    return prod_dict


# _______________
# specialized serializers


def serialize_stock(product):
    return {
        "pk": product.pk,
        "unit": product.unit,
        "manufacturer_style": product.manufacturer_style,
        "manufacturer_collection": product.manufacturer_collection,
        "manufacturer_sku": product.manufacturer_sku,
        "name": product.name,
        "swatch_image": product.swatch_image.url if product.swatch_image else None,
        "manufacturer": product.manufacturer.label,
        "low_price": getattr(product, "low_price", None),
    }


def serialize_warranty(product):
    return {
        "residential_warranty": product.residential_warranty,
        "commercial_warranty": product.commercial_warranty,
        "light_commercial_warranty": product.light_commercial_warranty,
    }


# def serialize_geometry(product: ProductSubClass):
#     dxf_file = product.dxf_file.url if product.dxf_file else None
#     dwg_3d_file = product.dwg_3d_file.url if product.dwg_3d_file else None
#     dwg_2d_file = product.dwg_2d_file.url if product.dwg_2d_file else None
#     obj_file = product.obj_file.url if product.obj_file else None
#     mtl_file = product.mtl_file.url if product.mtl_file else None
#     gltf_file = product.gltf_file.url if product.gltf_file else None
#     stl_file = product.stl_file.url if product.stl_file else None
#     dae_file = product.dae_file.url if product.dae_file else None
#     rfa_file = product.rfa_file.url if product.rfa_file else None
#     ipt_file = product.ipt_file.url if product.ipt_file else None
#     if not obj_file:
#         obj_file = product.derived_obj_file.url if product.derived_obj_file else None
#     if not mtl_file:
#         mtl_file = product.derived_mtl_file.url if product.derived_mtl_file else None
#     if not gltf_file:
#         gltf_file = product.derived_gltf_file.url if product.derived_gltf_file else None
#     if not stl_file:
#         stl_file = product.derived_stl_file.url if product.derived_stl_file else None
#     if not dae_file:
#         dae_file = product.derived_dae_file.url if product.derived_dae_file else None

#     return {
#         'width': product.get_width(),
#         'depth': product.get_depth(),
#         'height': product.get_height(),
#         'dxf_file': dxf_file,
#         'dwg_3d_file': dwg_3d_file,
#         'dwg_2d_file': dwg_2d_file,
#         'obj_file': obj_file,
#         'mtl_file': mtl_file,
#         'gltf_file': gltf_file,
#         'stl_file': stl_file,
#         'dae_file': dae_file,
#         'rfa_file': rfa_file,
#         'ipt_file': ipt_file,
#         'three_json': product.three_json,
#         'geometry_clean': product.geometry_clean
#     }


# def encode_image(url: str):
# image = image.open()
# with image.open() as img_file:
#     print(img_file)
#     encoded_string = base64.b64encode(img_file.red())
# return f'data:image/png; base64, {encoded_string}'

# if product.tiling_image:
#     image = product.tiling_image.url
# image = get_storage_class().base_path() + image

# image = encode_image(image)
# image = product.swatch_image.url if product.swatch_image else None
# content = requests.get(url).content
# ary = np.array(content)
# r, g, b = np.split(ary, 3, axis=2)
# r = r.reshape(-1)
# g = g.reshape(-1)
# b = b.reshape(-1)
# bitmap = list(map(lambda x: 0.299*x[0]+0.587*x[1]+0.114*x[2],
# zip(r,g,b)))
# bitmap = np.array(bitmap).reshape([ary.shape, ary.shape])
# bitmap = np.dot((bitmap > 128).astype(float),255)
# image = pimage.fromarray(bitmap.astype(np.uint8))
