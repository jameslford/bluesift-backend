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
        next_link = results.get('@odata.nextLink', None)
        items = results['value']
        for item in items:
            product = ScraperFinishSurface()
            product.subgroup = self.subgroup
            style_number = item['SellingStyleNbr']
            product.manufacturer_sku = item.get('UniqueId', None)
            product.manufacturer_collection = item.get('SellingStyleName', None)
            product.manufacturer_style = item.get('SellingColorName', None)
            base_product_url = self.base_url + '/flooring'
            product.product_url = (
                f'{base_product_url}/{self.subgroup.category.name}/details/'
                f'{"-".join(product.manufacturer_collection.strip().split(" "))}-{style_number}/'
                f'{"-".join(product.manufacturer_style.strip().split(" "))}'
            )
            # vignette = item['Vignette']
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
        # if next_link:
        #     new_link = str(next_link.strip('"'))
        #     print(new_link)
        #     new_link = None
        #     self.get_data(new_link)
        self.subgroup.scraped = True
        self.subgroup.save()

    def clean(self):
        from Scraper.ScraperFinishSurface.models import ScraperFinishSurface
        default_tiles = ScraperFinishSurface.objects.using('scraper_default').filter(material='stone & glass')
        revised_tiles = ScraperFinishSurface.objects.filter(material='stone & glass')
        for tile in default_tiles:
            default_look = tile.look
            revised_product: ScraperFinishSurface = revised_tiles.get(pk=tile.pk)
            if not default_look:
                continue
            if 'mosaic' in default_look.lower():
                revised_product.shape = 'mosaic'
            if 'glass' in default_look.lower():
                revised_product.sub_material = 'glass'
            revised_product.save()
