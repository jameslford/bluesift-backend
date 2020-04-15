import requests
from bs4 import BeautifulSoup
from Scraper.models import ScraperGroup
from SpecializedProducts.models import Range



def run(group: ScraperGroup):
    url = group.base_url
    data = requests.get(url).text
    base = 'https://www.vikingrange.com'
    soup = BeautifulSoup(data, 'lxml')
    figures = soup.find_all('figure')
    for figure in figures:
        anch = figure.find('figcaption').find('a')
        name = anch.text
        name_split = name.split('-')
        if len(name_split) > 1:
            name = name_split[0]
        img = figure.find('img')
        pid = figure.find('input', {'class': 'comparison-product-id'})['value']
        path = base + anch['href'].split(';')[0]
        cad_path = f'https://www.vikingrange.com/consumer/products/tabs/product_specs_tab.jsp?id={pid}'
        options_pth = f'https://www.vikingrange.com/consumer/products/tabs/product_options_tab.jsp?id={pid}'
        options_req = requests.get(options_pth)
        options_soup = BeautifulSoup(options_req.text, 'lxml')
        options_rec = []
        options = options_soup.find_all('li')
        for option in options:
            vimg = option.find('img')
            title = option.find('h4')
            if vimg and title:
                options_rec.append({'src': img.get('src'), 'title': title.text})
        download_req = requests.get(cad_path)
        download_soup = BeautifulSoup(download_req.text, 'lxml')
        downloads = download_soup.find('div', {'class': 'design-software-symbols container clearfix'})
        links = downloads.find_all('a')
        links = [link.get('href') for link in links]
        links = [link for link in links if '3DFiles' in link]
        for rec in options_rec:
            sku = rec.get('title')
            variation_img = rec.get('src')
            search = sku.replace('-', '')
            rec_downloads = []
            img_src = img.get('src')
            product: Range = Range()
            product.scraper_group = group
            product.manufacturer = group.manufacturer
            product.manufacturer_sku = sku
            if img_src:
                print(img_src)
                product.swatch_image_original = img_src
            product.room_scene_original = variation_img
            product.manufacturer_url = path
            for link in links:
                if search in link:
                    if not link.startswith(base):
                        link = base + link
                    rec_downloads.append(base + link)
            for download in rec_downloads:
                if download.endswith('obj.zip'):
                    product.obj_file = download
                elif download.endswith('_.DWG'):
                    product.dwg_3d_file = download
                elif download.endswith('.dwg'):
                    product.dwg_2d_file = download
                elif download.endswith('_.DXF'):
                    product.dxf_file = download
                elif download.endswith('_.rfa'):
                    product.rfa_file = download
            if product.obj_file:
                product.name = name
                product.scraper_save()
            else:
                try:
                    product.delete()
                except AssertionError:
                    continue
