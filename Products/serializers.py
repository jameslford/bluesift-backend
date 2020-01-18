from typing import Dict
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
    return {
        'width': geometries.get('width'),
        'length': geometries.get('length'),
        'thickness': geometries.get('thickness'),
        'obj_file': product.obj_file.url if product.obj_file else None,
        'gltf_file': product.gltf_file.url if product.gltf_file else None,
        'stl_file': product.stl_file.url if product.stl_file else None,
        'rvt_file': product.rvt_file.url if product.rvt_file else None,
        'ipt_file': product.ipt.url if product.ipt_file else None,
        'dae_file': product.dae_file.url if product.dae_file else None,
        'three_json': product.three_json,
        'geometry_clean': product.geometry_clean
    }
