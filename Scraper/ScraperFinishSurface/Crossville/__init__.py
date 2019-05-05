import sys
import importlib
import requests
from ScraperBaseProduct.models import AggregateProductRating
from BSscraper.supers import SubScraperBase
from BSscraper.utils import clean_value
from ScraperFinishSurface.models import ScraperFinishSurface

class Scraper(SubScraperBase):
    base_url = 'https://www.crossvilleinc.com'

    def get_data(self):
        results = requests.get(self.subgroup.base_scraping_url).json()        
        for item in results:
            look = item.get('Style', None)
            if look:
                look = look.strip().lower()
            if 'ucco' in look:
                look = 'shaded / specked'
            if look:
                look = look.lower()
            if look == 'linear':
                look = 'natural pattern'
            if look == 'mingle':
                look = 'shaded / specked'
            if look == '3d':
                look = 'solid color'
            if look == 'natural stone':
                look = 'stone'
            if look == 'concrete':
                look = 'stone'
            if look == 'old world':
                look = 'shaded / specked'
            if look == 'mixed media':
                look = 'geometric pattern'

            submaterial = item['Material'].lower()
            if 'porcelain' in submaterial:
                submaterial = 'porcelain'
            if 'ceramic' in submaterial:
                submaterial = 'ceramic'

            manufacturer_collection = item['Collection']
            manufacturer_style = item['Color']
            product_url = self.base_url + item['Path']
            variants = item.get('StockingSkus', None)
            if not variants:
                continue

            for var in variants:
                product = ScraperFinishSurface()
                product.subgroup = self.subgroup
                trim_type = var.get('TrimType', None)
                if not trim_type:
                    trim_type = None
                elif 'Cove Base' in trim_type:
                    product.covebase = True
                elif 'Bullnose' in trim_type:
                    product.bullnose = True
                else:
                    trim_type = None

                applications = var.get('Applications', None)
                if not applications or trim_type:
                    continue
                swatch_image = self.base_url + var['Image']
                pattern_type = var.get('PatternType', None)
                if pattern_type and pattern_type == 'Mosaic':
                    submaterial = 'Mosaic ' + submaterial

                product.look = look
                product.material = 'stone & glass'
                product.sub_material = submaterial
                product.manufacturer_collection = manufacturer_collection
                product.manufacturer_style = manufacturer_style
                product.product_url = product_url
                product.finish = var['Finish']
                product.shade_variation = var.get('ShadeVariation', None)
                product.swatch_image_original = swatch_image
                product.thickness = clean_value(var['Thickness'])
                product.manufacturer_sku = var['Sku']
                size = var['Size'].split('x')
                if len(size) > 1:
                    product.width = clean_value(size[0])
                    product.length = clean_value(size[1])

                for app in applications:
                    product.floors = True if 'Interior floors dry' in app else False
                    product.walls = True if 'Interior walls dry' in app else False
                    product.counter_tops = True if 'Counters' in app else False
                    product.shower_floors = True if 'Interior floors wet' in app else False
                    product.shower_walls = True if 'Interior walls wet' in app else False
                    product.covered_walls = True if 'Exterior covered walls' in app else False
                    product.exterior_walls = True if 'Exterior walls' in app else False
                    product.pool_lining = True if 'Pool fountain full lining' in app else False

                
                product = product.name_sku_check()
                if not product:
                    continue
        self.subgroup.scraped = True
        self.subgroup.save()





              


