import json
import requests
from config.scripts.measurements import clean_value
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from . import MOHAWK_HEADER


def api_response(url):
    body = {
        "families": [
            "tile"
        ],
        "page": 0,
        "pageSize": 196,
        "facets": {
            "colors.specifications.Shade": [
                "light",
                "medium",
                "dark"
            ]
        },
        "sorting": "relevance",
        "query": "",
        "useColorsIndex": True
        }


    header = MOHAWK_HEADER
    response = requests.post(url, data=json.dumps(body), headers=header).json()
    return response

def get_special(product: ScraperFinishSurface, item):
    product.material = 'stone & glass'
    return product

def get_special_detail(text):
    colors = text['colors']
    products = []
    for color in colors:
        manufacturer_color = color.get('colorName', None)
        color_spec = color['specifications']
        gloss = color_spec.get('gloss', None)
        matte = color_spec.get('matte', None)
        sizes = color['sizes']
        for size in sizes:
            product = ScraperFinishSurface()
            product.material = 'stone & glass'
            product.manufacturer_style = manufacturer_color
            product.width = clean_value(size.get('length', None))
            product.length = clean_value(size.get('width', None))
            size_type = size.get('sizeType', '').lower()
            if 'bullnose' in size_type:
                product.bullnose = True
            if gloss == 'True':
                product.finish = 'gloss'
            if matte == 'True':
                product.finish = 'matte'
            size_spec = size['specifications']
            product.sub_material = size_spec.get('material', None)
            product.shade_variation = size_spec.get('shade Variation', None)
            thickness = size_spec.get('thickness', None)
            if thickness:
                product.thickness = clean_value(thickness.replace('\"', ''))
            product.countertops = True if size_spec.get('countertops', '') == 'True' else False
            product.floors = True if size_spec.get('floor', '') == 'True' else False
            product.walls = True if size_spec.get('wall', '') == 'True' else False
            product.commercial = True if size_spec.get('commercial', '') == 'True' else False
            exterior = True if size_spec.get('outdoor', '') == 'True' else False
            cover = True if size_spec.get('coveredOutdoor', '') == 'True' else False
            if exterior:
                product.exterior_floors = True if product.floors else False
                product.exterior_walls = True if product.walls else False
            images = size['images']
            swatches = images.get('swatch', None)
            if not swatches:
                continue
            product.swatch_image_original = images['swatch'][0]['path']
            room_scenes = images.get('roomScene', None)
            if room_scenes:
                product.room_scene_original = room_scenes[0]['path']
            products.append(product)
    return products
            


            




