import requests
import decimal
from SpecializedProducts.models import FinishSurface
from utils.measurements import clean_value
from Scraper.models import ScraperGroup


def scrape(group: ScraperGroup, get_special):
    base_url = "https://shawfloors.com"
    url = group.base_url
    results = requests.get(url).json()
    # next_link = results.get('@odata.nextLink', None)
    items = results["value"]
    for item in items:
        model = group.get_model()
        product: FinishSurface = model()
        product.scraper_group = group
        product.manufacturer = group.manufacturer
        style_number = item["SellingStyleNbr"]
        product.manufacturer_sku = item.get("UniqueId", None)
        product.manufacturer_collection = item.get("SellingStyleName", None)
        product.manufacturer_style = item.get("SellingColorName", None)
        base_manufacturer_url = base_url + "/flooring"
        manufacturer_url = (
            f"{base_manufacturer_url}/{group.module_name}/details/"
            f'{"-".join(product.manufacturer_collection.strip().split(" "))}-{style_number}/'
            f'{"-".join(product.manufacturer_style.strip().split(" "))}'
        )
        product.manufacturer_url = manufacturer_url.replace("+", "")
        image = (
            f"https://shawfloors.scene7.com/is/image/ShawIndustries/"
            f"{product.manufacturer_sku}"
            f"_MAIN?id=kcRrj3&amp;fmt=jpg&amp;fit=constrain,1&amp;wid=998&amp;hei=998"
        )
        image2 = (
            f"https://shawfloors.scene7.com/is/image/ShawIndustries/{product.manufacturer_sku}_ROOM"
            f"?fmt=Jpeg&qlt=60&wid=1024"
        )
        try:
            product.thickness = decimal.Decimal(clean_value(item["Thickness"]))
        except TypeError:
            print("couldnt convert")
        product = get_special(product, item)
        product.swatch_image_original = image
        product.room_scene_original = image2
        light_com = item.get("LightComWarranty", None)
        if light_com:
            product.light_commericial_warranty = light_com
        residential_warranty = item.get("Warranty", None)
        if residential_warranty:
            product.residential_warranty = residential_warranty
        product.scraper_save()


# def clean(self):
#     clean_func = self.get_clean_func()
#     products = self.subgroup.get_products()
#     for product in products:
#         if clean_func:
#             print('running clean func for ' + self.subgroup.__str__())
#             clean_func(product)
