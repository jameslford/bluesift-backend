import json
import requests
from config.scripts.measurements import clean_value
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
from . import MOHAWK_HEADER

def api_response(url):
    body = {
        "families": [
            "lvt"
        ],
        "page": 0,
        "pageSize": 219,
        "facets": {
            "colors.specifications.StoneOrWood": [
                "stone",
                "wood"
            ]
        },
        "sorting": "relevance",
        "query": "",
        "useColorsIndex": True
    }

    response = requests.post(url, data=json.dumps(body), headers=MOHAWK_HEADER).json()
    return response

def get_special_detail(text):
    product = ScraperFinishSurface()
    specs = text['specifications']
    material = 'vinyl'
    sub_material = specs.get('construction', '') + ' vinyl'
    thickness = specs.get('thickness', None)
    thickness = clean_value(thickness)
    installation = specs.get('vinyl Installation', None)
    size = specs.get('size', None)
    width = None
    length = None
    if size:
        size = size.split('x')
        if len(size) > 1:
            width = size[0].replace("\\", '')
            length = size[1].replace("\\", '')
    commercial_warranty = specs.get('commercialWarranty', None)
    product.cof = specs.get('static Coefficient of Friction', None)
    rollwidth = specs.get('roll Width', None)
    colors = text.get('colors', None)
    if not colors:
        return
    products = []
    for color in colors:
        product = ScraperFinishSurface()
        product.manufacturer_style = color['colorName']
        color_spec = color['specifications']
        product.floors = True
        product.material = material
        product.sub_material = sub_material
        product.commercial_warranty = commercial_warranty
        product.thickness = thickness
        product.residential_warranty = color_spec.get('residentialWarranty', None)
        look = color_spec.get('stoneOrWood', None)
        product.install_type = installation
        product.look = look
        if rollwidth:
            product.width = clean_value(rollwidth)
        elif width:
            product.width = clean_value(width)
        product.length = length
        images = color['images']
        swatch_images = images.get('swatch', None)
        if not swatch_images:
            continue
        product.swatch_image_original = swatch_images[0]['path']
        room_scene = images.get('roomScene', None)
        if room_scene:
            product.room_scene_original = room_scene[0]['path']
        products.append(product)
    return products

    # product.material = 'vinly'
    # thickness = clean_value(specs.get('thickness', None))
    # material = specs.get('product Type', 'vinyl')
    # look = specs.get('stoneOrWood', None)
