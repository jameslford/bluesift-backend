import requests
from bs4 import BeautifulSoup
from Scraper.models import ScraperGroup
from SpecializedProducts.models import Oven, ApplianceColor



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
        img = img['src'] if img else None
        pid = figure.find('input', {'class': 'comparison-product-id'})['value']
        path = base + anch['href'].split(';')[0]
        cad_path = f'https://www.vikingrange.com/consumer/products/tabs/product_specs_tab.jsp?id={pid}'
        details_path = f'https://www.vikingrange.com/consumer/products/tabs/product_overview_tab.jsp?id={pid}'
        details_res = requests.get(details_path).text
        details_soup = BeautifulSoup(details_res, 'lxml')
        sku = details_soup.find(id='sku-name-div').text
        finishes = details_soup.find_all('label', class_='product-finish-item')
        finishes = finishes if finishes else []
        full_soup = requests.get(path)
        full_soup = BeautifulSoup(full_soup.text, 'lxml')
        series = full_soup.find('section', class_="details header-page clearfix")
        name = series.find('h1').text.split('-')[0].strip()
        series = series.find('span').text.strip().replace('viking', '')
        colors = []
        for finish in finishes:
            style = finish['style']
            bgColor = style.replace('background-color', '').strip() if style and 'background-color' in style else None
            text = finish.find('span').text.strip()
            if bgColor and text:
                color = ApplianceColor.objects.get_or_create(
                    manufacturer=group.manufacturer,
                    hex_value=bgColor,
                    name=text
                    )[0]
                colors.append(color)

        download_req = requests.get(cad_path)
        download_soup = BeautifulSoup(download_req.text, 'lxml')
        downloads = download_soup.find('div', {'class': 'design-software-symbols container clearfix'})
        links = downloads.find_all('a') if downloads else []
        links = [link.get('href') for link in links]
        links = [link for link in links if '3DFiles' in link]
        product = Oven()
        product.manufacturer_sku = sku
        product.name = name
        product.manufacturer_collection = series
        product.manufacturer_url = path
        product.swatch_image_original = img
        product.manufacturer = group.manufacturer
        product.finishes = ['stainless steel']
        product.fuel_type = 'electric'
        for download in links:
            if not download.startswith(base):
                download = base + download
            if not product.obj_file and download.endswith('obj.zip'):
                product.obj_file = download
            elif not product.dwg_3d_file and download.endswith('_.DWG'):
                product.dwg_3d_file = download
            elif not product.dwg_2d_file and download.endswith('.dwg'):
                product.dwg_2d_file = download
            elif not product.dxf_file and download.endswith('_.DXF'):
                product.dxf_file = download
            elif not product.rfa_file and download.endswith('_.rfa'):
                product.rfa_file = download
        print(sku)
        print('______________________')
        product = product.scraper_save()
        # product.refresh_from_db()
        product.colors.add(*colors)
