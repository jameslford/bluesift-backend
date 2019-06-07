import sys
import importlib
import requests
import json
from Scraper.models import ScraperAggregateProductRating, SubScraperBase
from config.scripts.measurements import clean_value
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

class Scraper(SubScraperBase):
    base_url = 'www.floridatile.com'
    init_url = 'https://www.floridatile.com/product-search/'
    api_url = 'https://www.floridatile.com/api/public/v1/'
    pages = range(1, 17)


    def get_data(self):
        for page in self.pages:
            body = {
                'action': "tile_search",
                'microban_filter': None,
                'page': page,
                'residentialSwitch': True
            }
            session = requests.Session()
            response = session.get(self.init_url)
            cookies = session.cookies.get_dict()
            csrf_token = cookies['csrftoken']
            headers = {
                'x-csrftoken': csrf_token,
                'cookies': 'csrftoken=' + csrf_token,
                'referer': self.init_url,
                'origin': self.base_url
            }
            response = session.post(self.api_url, data=json.dumps(body), headers=headers)
            data = response.json().get('data', None)
            for item in data:
                product = ScraperFinishSurface()
                product.subgroup = self.subgroup
                product.material = 'stone & glass'
                product.manufacturer_collection = item['series']
                product.manufacturer_style = item['color']
                product.manufacturer_sku = item['sku']
                product.product_url = item['series_url']
                product.swatch_image_original = item['original_image']
                product.web_id = item['id']
                size = item['size'].split('x')
                if len(size) > 1:
                    product.width = clean_value(size[0])
                    product.length = clean_value(size[1])
                product = self.get_detail(product)
                product = product.name_sku_check()
        self.subgroup.scraped = True
        self.subgroup.save()



    def get_detail(self, product: ScraperFinishSurface):
        session = requests.Session()
        response = session.get(self.init_url)
        cookies = session.cookies.get_dict()
        csrf_token = cookies['csrftoken']
        headers = {
            'x-csrftoken': csrf_token,
            'cookies': 'csrftoken=' + csrf_token,
            'referer': self.init_url,
            'origin': self.base_url
        }
        body = {
            'action': "get_tile_data",
            'sku': product.manufacturer_sku,
            'tile': None
        }
        response = session.post(self.api_url, data=json.dumps(body), headers=headers)
        print(response)
        data = response.json()['data']
        product.sub_material = data['body_composition']
        product.edge = data['edge']
        product.look = data['look']
        product.shade_variation = data['shade_variation']
        product.thickness = clean_value(data['thickness'])
        product.walls = True
        application = data['application']
        if 'Floor' in application:
            product.floors = True
        return product
