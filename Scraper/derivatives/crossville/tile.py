import requests
from psycopg2.extras import NumericRange
from utils.measurements import clean_value
from SpecializedProducts.models import TileAndStone
from Scraper.models import ScraperGroup


def run(group: ScraperGroup):
    results = requests.get(group.base_url).json()
    base_url = "https://www.crossvilleinc.com/"
    for item in results:
        look = item.get("Style", None)
        if look:
            look = look.strip().lower()
        if "ucco" in look:
            look = "shaded / specked"
        if look:
            look = look.lower()
        if look == "linear":
            look = "natural pattern"
        if look == "mingle":
            look = "shaded / specked"
        if look == "3d":
            look = "solid color"
        if look == "natural stone":
            look = "stone"
        if look == "concrete":
            look = "stone"
        if look == "old world":
            look = "shaded / specked"
        if look == "mixed media":
            look = "geometric pattern"

        submaterial = item["Material"].lower()
        if "porcelain" in submaterial:
            submaterial = "porcelain"
        if "ceramic" in submaterial:
            submaterial = "ceramic"

        manufacturer_collection = item["Collection"]
        manufacturer_style = item["Color"]
        manufacturer_url = base_url + item["Path"]
        variants = item.get("StockingSkus", None)
        if not variants:
            continue

        for var in variants:
            applications = var.get("Applications", None)
            if not applications:
                continue
            product = TileAndStone()
            swatch_image = base_url + var["Image"]
            pattern_type = var.get("PatternType", None)
            if pattern_type and pattern_type == "Mosaic":
                product.shape = "mosaic"
            product.scraper_group = group
            product.look = look
            product.manufacturer = group.manufacturer
            product.material_type = submaterial
            product.manufacturer_collection = manufacturer_collection
            product.manufacturer_style = manufacturer_style
            product.manufacturer_url = manufacturer_url
            product.finish = var["Finish"]
            product.shade_variation = var.get("ShadeVariation", None)
            product.swatch_image_original = swatch_image
            product.thickness = clean_value(var["Thickness"])
            print("thickness = ", product.thickness)
            product.manufacturer_sku = var["Sku"]
            size = var["Size"].split("x")
            print(size)
            if len(size) > 1:
                product.width = NumericRange(clean_value(size[0]))
                product.length = NumericRange(clean_value(size[1]))
            print(product.width, product.length, product.thickness)
            if not (product.thickness and product.width and product.length):
                print("bad values")
                continue

            product.floors = bool("Interior floors dry" in applications)
            product.walls = bool("Interior walls dry" in applications)
            product.counter_tops = bool("Counters" in applications)
            product.shower_floors = bool("Interior floors wet" in applications)
            product.shower_walls = bool("Interior walls wet" in applications)
            product.covered_walls = bool("Exterior covered walls" in applications)
            product.exterior_walls = bool("Exterior walls" in applications)
            product.pool_lining = bool("Pool fountain full lining" in applications)
            product.scraper_save()


def clean(product: TileAndStone):
    if (
        product.width
        and product.width.lower
        and product.length
        and product.length.lower
    ):
        if product.width.lower * product.length.lower <= 8:
            product.scale_length = 12
            product.scale_width = 12
    return product


def crossvile_measurement(value: str) -> str:
    new_val = value.replace("+", "")
    new_val = new_val.replace("panel", "")
    new_val = new_val.strip()
    length_split = new_val.split(" ")
    unit = length_split.pop(-1)
    recomb = 0
    for measure in length_split:
        _measure = measure
        if "/" in measure:
            msplit = _measure.split("/")
            num = float(msplit[0]) / float(msplit[1])
            _measure = round(num, 2)
        else:
            _measure = round(float(measure), 2)
        recomb += _measure
    if "mm" in unit:
        recomb = round((recomb / 25.4), 2)
    elif "m" in unit:
        recomb = round((recomb * 39.37), 2)
    return str(round(recomb, 2))
