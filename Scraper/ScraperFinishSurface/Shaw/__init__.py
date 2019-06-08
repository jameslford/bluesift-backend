import sys
import importlib
import requests
from config.scripts.measurements import clean_value
from Scraper.models import SubScraperBase
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface



class Scraper(SubScraperBase):
    base_url = 'https://shawfloors.com'

    def get_data(self, url=None):
        if not url:
            url = self.subgroup.base_scraping_url
        results = requests.get(url).json()
        # next_link = results.get('@odata.nextLink', None)
        items = results['value']
        for item in items:
            product = ScraperFinishSurface()
            product.subgroup = self.subgroup
            style_number = item['SellingStyleNbr']
            product.manufacturer_sku = item.get('UniqueId', None)
            product.manufacturer_collection = item.get('SellingStyleName', None)
            product.manufacturer_style = item.get('SellingColorName', None)
            base_product_url = self.base_url + '/flooring'
            product_url = (
                f'{base_product_url}/{self.subgroup.category.name}/details/'
                f'{"-".join(product.manufacturer_collection.strip().split(" "))}-{style_number}/'
                f'{"-".join(product.manufacturer_style.strip().split(" "))}'
            )
            product.product_url = product_url.replace('+', '')
            image = (
                f'https://shawfloors.scene7.com/is/image/ShawIndustries/'
                f'{product.manufacturer_sku}'
                f'_MAIN?id=kcRrj3&amp;fmt=jpg&amp;fit=constrain,1&amp;wid=998&amp;hei=998'
                )
            image2 = (
                f'https://shawfloors.scene7.com/is/image/ShawIndustries/{product.manufacturer_sku}_ROOM'
                f'?fmt=Jpeg&qlt=60&wid=1024'
                )
            product = self.get_sub_function(product, item)
            product.swatch_image_original = image
            product.room_scene_original = image2
            light_com = item.get('LightComWarranty', None)
            if light_com:
                product.light_commericial_warranty = light_com
            residential_warranty = item.get('Warranty', None)
            if residential_warranty:
                product.residential_warranty = residential_warranty
            product.name_sku_check()
        self.subgroup.scraped = True
        self.subgroup.save()

    def clean(self):
        clean_func = self.get_clean_func()
        products = self.subgroup.get_products()
        for product in products:
            if clean_func:
                print('running clean func for ' + self.subgroup.__str__())
                clean_func(product)

