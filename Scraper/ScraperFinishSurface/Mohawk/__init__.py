import sys
import importlib
import json
import requests
import lxml
from bs4 import BeautifulSoup
from Scraper.models import SubScraperBase
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

MOHAWK_HEADER = {
    'Host': 'www.mohawkflooring.com',
    'Accept': 'application/json, text/plain, */*',
    'Origin': 'https://www.mohawkflooring.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36',
    'Content-Length': '181',
    'Request-Id': '|KnKLv.pF5aL',
    'Content-Type': 'application/json',
    'Cookie': 'ASP.NET_SessionId=flouq2e2ntifrfwgaolav23z; SC_ANALYTICS_GLOBAL_COOKIE=3653867d0b6d4ca39d8cbd6bbda6eaef|False; ai_user=Ty7h2|2018-09-13T20:42:28.847Z; ffvisitorids={"mohawk_flooring":"f4540fd6c1804c8ab0ed0becd58bc9be"}; _hjIncludedInSample=1; _ga=GA1.2.541790398.1536871350; _gid=GA1.2.1955447638.1536871350; __distillery=7fb6149_b5546593-57bd-415c-928f-09c0f9d6177f-2b4ee6130-ca7e159a345e-c649; ai_session=HF+MQ|1536871349575|1536871855570.8; _gat_UA-22103287-1=1',
    'Request-Context': 'appId=cid-v1:4bd04b6a-18c8-4b54-a73f-69caadc9495d',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Referer': 'https://www.mohawkflooring.com/carpet/search?page=2'
    }

class Scraper(SubScraperBase):
    base_url = 'https://www.mohawkflooring.com'
    urls = []

    def get_data(self):
        print('getting')
        response = self.get_sub_response()
        results = response['results']
        for result in results:
            collection = result['styleName']
            style_url = self.base_url + result['pdpUrl']
            print(style_url)
            self.urls.append(style_url)
        for url in self.urls:
            self.get_detail(url, collection)
        self.subgroup.scraped = True
        self.subgroup.save()


    def get_detail(self, url, collection):
        response = requests.get(url).text
        soup = BeautifulSoup(response, 'lxml')
        div = soup.find('div', {'id': 'product-details'})
        if not div:
            print('no div')
            return
        scripts = div.find('script').text
        text = scripts.replace('var pdpInitData = ', '')
        text = text[:-6]
        text = json.loads(text)
        # print(text)
        text = text['style']
        func = self.get_sub_detail()
        products = func(text)
        if not products:
            return
        for product in products:
            product: ScraperFinishSurface = product
            product.subgroup = self.subgroup
            product.manufacturer_collection = collection
            product.product_url = url
            product.name_sku_check()
        return
