import io
import zipfile
import requests
from bs4 import BeautifulSoup
from django.core.files.base import ContentFile
from SpecializedProducts.models import Appliance
from Products.models import Manufacturer

category_map = {
    'range': {
        'id': 'id=cat12360038',
        },
    'refrigerator': {
        'id': 'id=cat12360054'
    }
}

def scrape(category: str):
    manufacturer = Manufacturer.objects.get_or_create(label='Viking')[0]
    cat_dict = category_map.get(category)
    if not category:
        raise Exception(f'{category} is not a valid category for viking')
    appliance_type = category
    web_id = cat_dict.get('id')
    url = f'https://www.vikingrange.com/consumer/products/tabs/subcategory_find_products_tab.jsp?{web_id}'
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
            product: Appliance = Appliance.objects.get_or_create(
                manufacturer=manufacturer,
                manufacturer_sku=sku,
                appliance_type=appliance_type)[0]
            if img_src:
                print(img_src)
                img_name = img_src.split('/')[-1]
                img_content = requests.get(img_src).content
                img_file = ContentFile(img_content)
                product.swatch_image.save(img_name, img_file)
            product.manufacturer_url = path
            if product.obj_file:
                product.save()
                continue
            for link in links:
                if search in link:
                    print(link)
                    rec_downloads.append(base + link)
            save = False
            for download in rec_downloads:
                if download.endswith('obj.zip'):
                    # download_obj_zip(download, product)
                    save = True
                    product.obj_file = download
                elif download.endswith('_.DWG'):
                    product.dwg_3d_file = download
                elif download.endswith('.dwg'):
                    product.dwg_2d_file = download
                elif download.endswith('_.DWG'):
                    product.dwg_3d_file = download
                elif download.endswith('_.rfa'):
                    product.rfa_file = download
                if save:
                    product.name = name
                    product.save()
                else:
                    try:
                        product.delete()
                    except AssertionError:
                        continue


# def download_obj_zip(download, product):
#     res = requests.get(download, stream=True)
#     try:
#         zipped = zipfile.ZipFile(io.BytesIO(res.content))
#     except zipfile.BadZipfile:
#         return
#     product.obj_file = download
#     for name in zipped.namelist():
#         if name.endswith('.obj'):
#             file = ContentFile(zipped.read(name))
#             product._obj_file.save(name, file, save=True)
#         if name.endswith('.mtl'):
#             file = ContentFile(zipped.read(name))
#             product._mtl_file.save(name, file, save=True)
