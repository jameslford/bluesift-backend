# import requests
# import zipfile
# import io
# from bs4 import BeautifulSoup
# from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from scrapers import route_scrape
# from Products.models import Manufacturer


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('manufacturer', type=str)
        parser.add_argument('category', type=str)


    def handle(self, *args, **options):
        manufacturer = options.get('manufacturer')
        category = options.get('category')
        route_scrape(manufacturer, category)
        # manufacturer = Manufacturer.objects.get_or_create(label='Viking')[0]
        # appliance_type = 'range'
        # url = 'https://www.vikingrange.com/consumer/products/tabs/subcategory_find_products_tab.jsp?id=cat12360038'
        # data = requests.get(url).text
        # base = 'https://www.vikingrange.com'
        # soup = BeautifulSoup(data, 'lxml')
        # figures = soup.find_all('figure')
        # for figure in figures:
        #     anch = figure.find('a')
        #     img = figure.find('img')
        #     pid = figure.find('input', {'class': 'comparison-product-id'})['value']
        #     path = base + anch['href'].split(';')[0]
        #     cad_path = f'https://www.vikingrange.com/consumer/products/tabs/product_specs_tab.jsp?id={pid}'
        #     options_pth = f'https://www.vikingrange.com/consumer/products/tabs/product_options_tab.jsp?id={pid}'
        #     options_req = requests.get(options_pth)
        #     options_soup = BeautifulSoup(options_req.text, 'lxml')
        #     options_rec = []
        #     options = options_soup.find_all('li')
        #     for option in options:
        #         vimg = option.find('img')
        #         title = option.find('h4')
        #         if vimg and title:
        #             options_rec.append({'src': img.get('src'), 'title': title.text})
        #     download_req = requests.get(cad_path)
        #     download_soup = BeautifulSoup(download_req.text, 'lxml')
        #     downloads = download_soup.find('div', {'class': 'design-software-symbols container clearfix'})
        #     links = downloads.find_all('a')
        #     links = [link.get('href') for link in links]
        #     links = [link for link in links if '3DFiles' in link]
        #     for rec in options_rec:
        #         sku = rec.get('title')
        #         variation_img = rec.get('src')
        #         search = sku.replace('-', '')
        #         rec_downloads = []
        #         img_src = img.get('src')
        #         product: Appliance = Appliance.objects.get_or_create(manufacturer=manufacturer, manufacturer_sku=sku, appliance_type=appliance_type)[0]
        #         if img_src:
        #             print(img_src)
        #             img_name = img_src.split('/')[-1]
        #             img_content = requests.get(img_src).content
        #             img_file = ContentFile(img_content)
        #             product.swatch_image.save(img_name, img_file)
        #         product.manufacturer_url = path
        #         if product.obj_file:
        #             product.save()
        #             continue
        #         for link in links:
        #             if search in link:
        #                 print(link)
        #                 rec_downloads.append(base + link)

        #         for download in rec_downloads:
        #             if download.endswith('obj.zip'):
        #                 res = requests.get(download, stream=True)
        #                 zipped = zipfile.ZipFile(io.BytesIO(res.content))
        #                 product.obj_file = download
        #                 for name in zipped.namelist():
        #                     if name.endswith('.obj'):
        #                         file = ContentFile(zipped.read(name))
        #                         product._obj_file.save(name, file, save=True)
        #                         print(name, ' saved')
        #                     if name.endswith('.mtl'):
        #                         file = ContentFile(zipped.read(name))
        #                         product._mtl_file.save(name, file, save=True)
        #                         print(name, ' saved')
        #             elif download.endswith('_.DWG'):
        #                 product.dwg_3d_file = download
        #             elif download.endswith('.dwg'):
        #                 product.dwg_2d_file = download
        #             elif download.endswith('_.DWG'):
        #                 product.dwg_3d_file = download
        #             elif download.endswith('_.rfa'):
        #                 product.rfa_file = download
        #             product.save()

        #                 # extracted = {name: zipped.read(name) for name in zipped.namelist()}
        #                 # print(extracted)


