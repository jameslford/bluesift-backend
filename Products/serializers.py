from typing import Dict
from django.core.files.storage import get_storage_class
from .models import Product, ProductSubClass


def serialize_detail_quick(product):
    stock = serialize_stock(product)
    special = product.serialize_special()
    special.update({'warranty': serialize_warranty(product)})
    priced = [price.serialize_mini() for price in product.get_in_store_priced()]
    stock.update({
        'manufacturer_url': product.manufacturer_url,
        'room_scene': product.room_scene.url if product.room_scene else None,
        'priced': priced,
        'lists': special
        })
    return stock


def serialize_detail(product):
    stock = serialize_stock(product)
    special = product.serialize_special()
    special.update({'warranty': serialize_warranty(product)})
    priced = [price.serialize_mini() for price in product.get_in_store_priced()]
    stock.update({
        'manufacturer_url': product.manufacturer_url,
        'room_scene': product.room_scene.url if product.room_scene else None,
        'priced': priced,
        'geometry': serialize_geometry(product),
        'lists': special
        })
    return stock


def serialize_product(product: Product) -> Dict[str, any]:
    return {
        'pk': product.pk,
        'unit': product.unit,
        'manufacturer_style': product.manufacturer_style,
        'manu_collection': product.manu_collection,
        'manufacturer_sku': product.manufacturer_sku,
        'name': product.name,
        'swatch_url': product.swatch_image.url if product.swatch_image else None,
        'manufacturer__label': product.manufacturer.label,
        'low_price': getattr(product, 'low_price', None)
        }

def serialize_product_priced(product: Product) -> Dict[str, any]:
    prod_dict = serialize_product(product)
    prod_dict['suppliers'] = [prod.get_priced() for prod in product.priced.all()]
    return prod_dict


# _______________
# specialized serializers

def serialize_stock(product):
    return {
        'pk': product.pk,
        'unit': product.unit,
        'manufacturer_style': product.manufacturer_style,
        'manufacturer_collection': product.manu_collection,
        'manufacturer_sku': product.manufacturer_sku,
        'name': product.name,
        'swatch_image': product.swatch_image.url if product.swatch_image else None,
        'manufacturer': product.manufacturer.label,
        'low_price': getattr(product, 'low_price', None)
        }



def serialize_warranty(product):
    return {
        'residential_warranty': product.residential_warranty,
        'commercial_warranty': product.commercial_warranty,
        'light_commercial_warranty': product.light_commercial_warranty
        }


def serialize_geometry(product: ProductSubClass):
    geometries = product.geometries()
    image = product.swatch_image.url if product.swatch_image else None
    if product.tiling_image:
        image = product.tiling_image.url
    image = get_storage_class().base_path() + image
    return {
        'width': geometries.get('width'),
        'length': geometries.get('length'),
        'thickness': geometries.get('thickness'),
        'image': image,
        'obj_file': product.initial_obj_file.url if product.initial_obj_file else None,
        'mtl_file': product.initial_obj_file.url if product.initial_obj_file else None,
        'gltf_file': product.initial_gltf_file.url if product.initial_gltf_file else None,
        'stl_file': product.initial_stl_file.url if product.initial_stl_file else None,
        'rvt_file': product.initial_rvt_file.url if product.initial_rvt_file else None,
        'ipt_file': product.initial_ipt.url if product.initial_ipt_file else None,
        'dae_file': product.initial_dae_file.url if product.initial_dae_file else None,
        'three_json': product.three_json,
        'geometry_clean': product.geometry_clean
    }
