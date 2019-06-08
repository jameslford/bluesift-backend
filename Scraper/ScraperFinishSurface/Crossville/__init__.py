import sys
import importlib
import requests
from fractions import Fraction
from config.scripts.measurements import clean_value, unified_measurement
from Scraper.models import SubScraperBase
from Scraper.ScraperFinishSurface.models import ScraperFinishSurface

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
                    product.floors = bool('Interior floors dry' in app)
                    product.walls = bool('Interior walls dry' in app)
                    product.counter_tops = bool('Counters' in app)
                    product.shower_floors = bool('Interior floors wet' in app)
                    product.shower_walls = bool('Interior walls wet' in app)
                    product.covered_walls = bool('Exterior covered walls' in app)
                    product.exterior_walls = bool('Exterior walls' in app)
                    product.pool_lining = bool('Pool fountain full lining' in app)

                product = product.name_sku_check()
                if not product:
                    continue
        self.subgroup.scraped = True
        self.subgroup.save()

    def clean(self):
        default_products = ScraperFinishSurface.objects.using('scraper_default').filter(subgroup=self.subgroup)
        for default_product in default_products:
            default_product: ScraperFinishSurface = default_product
            sub_material: str = default_product.sub_material.lower()
            revised_product: ScraperFinishSurface = ScraperFinishSurface.objects.using(
                'scraper_revised').get(pk=default_product.pk)
            if 'mosaic' in sub_material:
                new_sub_material = sub_material.replace('mosaic', '')
                revised_product.sub_material = new_sub_material.strip()
                revised_product.shape = 'mosaic'
            if (default_product.shower_walls or
                default_product.covered_walls or
                default_product.exterior_walls):
                default_product.walls = True
            if (default_product.shower_floors or
                default_product.covered_floors or
                default_product.exterior_floors):
                default_product.floors = True
            if 'countertop' in sub_material:
                revised_product.sub_material = 'porcelain'
                revised_product.countertops = True
            length = default_product.length
            if length:
                length = crossvile_measurement(length)
            thickness = default_product.thickness
            if thickness:
                thickness = crossvile_measurement(thickness)
            revised_product.thickness = thickness
            revised_product.length = length
            revised_product.save()


def crossvile_measurement(value: str) -> str:
    new_val = value.replace('+', '')
    new_val = new_val.replace('panel', '')
    new_val = new_val.strip()
    length_split = new_val.split(' ')
    unit = length_split.pop(-1)
    recomb = 0
    for measure in length_split:
        _measure = measure
        if '/' in measure:
            msplit = _measure.split('/')
            num = float(msplit[0]) / float(msplit[1])
            _measure = round(num, 2)
        else:
            _measure = round(float(measure), 2)
        recomb += _measure
    if 'mm' in unit:
        recomb = round((recomb / 25.4), 2)
    elif 'm' in unit:
        recomb = round((recomb * 39.37), 2)
    return str(round(recomb, 2))
