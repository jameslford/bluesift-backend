import json
import requests
from BSscraper.utils import clean_value
from ScraperFinishSurface.models import ScraperFinishSurface
from . import MOHAWK_HEADER

def api_response(url):
    body = {
        "families": [
            "laminate",
            "hardwood"
        ],
        "page": 0,
        "pageSize": 509,
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

    response = requests.post(url, data=json.dumps(body), headers=MOHAWK_HEADER)
    print(response)
    return response.json()

def get_special(product: ScraperFinishSurface, item):
    technology = item['technology']
    product.floors = True
    if technology == 'RevWood':
        product.material = 'engineered hardwood'
        product.sub_material = technology
    elif technology == 'TecWood':
        product.material = 'engineered hardwood'
        product.sub_material = technology
    elif technology == 'RevWood Plus':
        product.material = 'engineered hardwood'
        product.sub_material = technology
    else:
        product.material = 'solid hardwood'
    return product

def get_special_detail(text):
    specs = text['specifications']
    residential_warranty = specs.get('residentialWarranty', None)
    technology = specs.get('derivedWoodType', None)
    species = specs.get('appearance Species', None)
    if technology == 'RevWood':
        material = 'engineered hardwood'
        sub_material = technology
    elif technology == 'TecWood':
        material = 'engineered hardwood'
        sub_material = technology
    elif technology == 'RevWood Plus':
        material = 'engineered hardwood'
        sub_material = technology
    else:
        material = 'solid hardwood'
        sub_material = species
    width = specs.get('length', None)
    shade_variation = specs.get('shade Variation', None)
    length = specs.get('width', None)
    thickness = specs.get('thickness', None)
    edge = specs.get('edge Profile', None)
    colors = text['colors']
    products = []
    for color in colors:
        product = ScraperFinishSurface()
        product.floors = True
        product.material = material
        product.sub_material = sub_material
        product.shade_variation = shade_variation
        product.sqft_per_carton = color['specifications'].get('square Feet Per Carton')
        product.width = clean_value(width)
        product.length = clean_value(length)
        product.thickness = clean_value(thickness)
        product.edge = edge
        product.residential_warranty = residential_warranty
        product.manufacturer_style = color['colorName']
        images = color['images']
        swatch_image = images['swatch'][0].get('path', None)
        if not swatch_image:
            continue
        product.swatch_image_original = swatch_image
        product.room_scene_original = images['roomScene'][0].get('path', '')
        products.append(product)
    return products
