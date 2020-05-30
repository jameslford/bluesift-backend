from typing import Dict
from .models import Product
from SpecializedProducts.models import ProductSubClass


def serialize_detail_quick(product: ProductSubClass):
    stock = serialize_stock(product)
    special = product.grouped_fields()
    special.update({"warranty": serialize_warranty(product)})
    stock.update(
        {
            "manufacturer_url": product.manufacturer_url,
            "room_scene": product.room_scene.url if product.room_scene else None,
            "priced": product.serialize_priced(),
            "lists": special,
        }
    )
    return stock


def serialize_detail(product: ProductSubClass, zipcode=None):
    stock = serialize_stock(product)
    special = product.grouped_fields()
    special.update({"warranty": serialize_warranty(product)})
    parents = [product._meta.verbose_name_plural] + [
        parent._meta.verbose_name_plural for parent in product._meta.get_parent_list()
    ]
    stock.update(
        {
            "parents": parents[::-1],
            "manufacturer_url": product.manufacturer_url,
            "room_scene": product.room_scene.url if product.room_scene else None,
            "priced": product.serialize_priced(zipcode),
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
