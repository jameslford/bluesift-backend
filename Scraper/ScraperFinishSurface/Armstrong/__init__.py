import sys
import importlib
import requests
from bs4 import BeautifulSoup
from Scraper.models import ScraperAggregateProductRating
from ...models import SubScraperBase
from config.scripts.measurements import clean_value
from ..models import ScraperFinishSurface

class Scraper(SubScraperBase):
    base_url = 'https://www.armstrongflooring.com'

    def get_data(self):
        results = requests.get(self.subgroup.base_scraping_url).json()
        items = results['items']
        for item in items:
            product = ScraperFinishSurface()
            product.subgroup = self.subgroup
            product.product_url = self.base_url + item.get('link', None)
            product.manufacturer_sku = item.get('sku', None)
            collection = item.get('lineName', None)
            if collection:
                product.manufacturer_collection = collection
            product.manufacturer_style = item['longName']
            product.swatch_image_original = item.get('src', None)
            product.floors = True
            if 'commercial' in self.subgroup.category.name:
                product.commercial = True
            product = self.get_sub_function(product, item)
            if not product:
                continue

            product = self.get_detail(product)
            product = product.name_sku_check()
            if not product:
                continue

            rating = item.get('rating', None)
            db = self.subgroup._state.db
            if rating:
                rating_count = rating.get('count', None)
                rating_value = rating.get('val', None)
                if rating_count and rating_value:
                    new_rating = ScraperAggregateProductRating()
                    new_rating.rating_value = rating_value
                    new_rating.rating_count = rating_count
                    new_rating.product_bbsku = product.bb_sku
                    new_rating.save(using=db)
        self.subgroup.scraped = True
        self.subgroup.save()


    def get_detail(self, product: ScraperFinishSurface):
        url = product.product_url
        data = requests.get(url).text
        soup = BeautifulSoup(data, 'lxml')
        func = self.get_sub_detail()
        if product.commercial:
            empty_dict = {}
            for com_table in soup.find_all('div', {'class': 'specs-table'}):
                for tr in com_table.find_all('tr'):
                    tds = tr.find_all('td')
                    if tds:
                        try:
                            empty_dict[tds[0].text.strip()] = tds[1].span.text.strip()
                        except AttributeError:
                            empty_dict[tds[0].text.strip()] = tds[1].text.strip()
            tiling_image = None
            for tag in soup.find_all('a', {'class': 'download-link'}):
                if 'Self Tiling' in tag['title']:
                    tiling_image = tag['href']
            product.tiling_scene_original = tiling_image
            product = func(product, empty_dict)
        else:
            image_div = soup.find('div', {'class': 'image-viewer__thumbnails'})
            if image_div:
                images = image_div.find_all('a')
                if len(images) > 1:
                    product.room_scene_original = images[1].get('href', None)
            res_tables = soup.find_all('table', {'class': 'table--definitions'})
            if not res_tables:
                return product
            data = {}
            for res_table in res_tables:
                res_tds = res_table.find_all('td')
                res_ths = res_table.find_all('th')
                res_td_count = len(res_tds)
                if res_td_count > 0:
                    for val in range(res_td_count):
                        label = res_ths[val].text.strip()
                        value = res_tds[val].text.strip()
                        data[label] = value
            product.residential_warranty = data.get('Residential Warranty', None)
            product.light_commercial_warranty = data.get('Light Commercial Warranty', None)
            product.commercial_warranty = data.get('Commercial Warranty', None)
            sqft_per_carton = data.get('Square Feet per Box', None)
            if not sqft_per_carton:
                sqft_per_carton = data.get('Coverage Per Carton', None)
            product.sqft_per_carton = sqft_per_carton
            product = func(product, data)
        return product


    def clean(self):
        clean_func = self.get_clean_func()
        products = self.subgroup.get_products()
        for product in products:
            if clean_func:
                print('running clean func for ' + self.subgroup.__str__())
                clean_func(product)
