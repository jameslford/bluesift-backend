import csv
import time
import os
import re
import html5lib

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup


MAIN_URL = 'https://www.daltile.com/products'
ROOT_URL = 'https://www.daltile.com'
EMPTY = ['empty']
PATH = os.getcwd()
FILE = PATH + "\\daltile-list3.csv"

DRIVER = webdriver.Chrome()
DRIVER.get(MAIN_URL)



def run(page_number=1):

    urls = []
    page_counter = 0

    while page_counter < page_number:
        try:
            element = WebDriverWait(DRIVER, 100).until(
                EC.invisibility_of_element_located((By.ID, "loadingContent"))
                )
            print(page_counter)
        finally:
            pass
        time.sleep(2)
        soup_level1 = BeautifulSoup(DRIVER.page_source, 'html5lib')
        for link in soup_level1.find_all('a','product-url'):
            product_url = str(link.get('href'))
            image_url = str(link.find(class_= 'product-thumb')['src'])
            product_name = str(link.find(class_= 'section__item--heading').contents[0]).strip()
            urls.append([ROOT_URL+product_url, image_url, product_name])
        button = DRIVER.find_element_by_xpath("//img[@src='/Assets/Daltile/Images/pagination-right.png']")
        button.click()
        page_counter += 1

    for url in urls:
        DRIVER.get(url[0])
        time.sleep(1)
        soup_2 = BeautifulSoup(DRIVER.page_source, 'html5lib')
        product_info = soup_2.find("div", {"class": "info__content--text"})
        top_banner = soup_2.find("div", {"class": "breadcrumb-banner"})
        product_table = soup_2.find("div", {"class": "product-information__table"})

        applications = get_applications(product_table)
        description = get_descriptions(product_info)
        sizes = get_size(product_table)
        finish = get_finish(product_table)
        for size in sizes:
            with open(FILE, 'a') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(url)


def get_finish(product_table):
    if product_table:
        div = product_table.find("div", {"class": "finish-content"})
        if div:
            cont = div.contents[1]
            if cont:
                return cont.contents
            else:
                return EMPTY
        else: 
            return EMPTY
    else:
        return EMPTY



def get_size(product_table):
    if product_table:
        sizes = product_table.find_all("div", {"class": "dimension-measure"})
        if sizes:
            size_list = []
            for size in sizes:
                cont = size.contents[0]
                dimensions = cont.split('x')
                size_list.append(dimensions)
            return size_list
        else:
            return EMPTY
    else:
        return EMPTY
                



def get_applications(product_table):
    if product_table:
        application_div = product_table.find("div", {"class": "sizes-dimension__all--text display__flex--lg-width"})
        if application_div:
            app_contents = application_div.find("div", {"class": "display__flex--padding"})
            if app_contents:
                apps = str(app_contents.contents).strip().replace('\\n','').strip()
                for character in ["['","']",'\\n','u200b/', '\\u200b']:
                    apps = apps.replace(character,'') 
                    list = apps.split('\\')
                    app_list = []
                    for l in list:
                        app_list.append(l.strip())
                    return app_list
            else:
                return EMPTY
        else:
            return EMPTY
    else:
        return EMPTY


def get_descriptions(product_info):
    if product_info:
        text = product_info.find('p').text
        if text:
            return text
        else:
            return EMPTY
    else:
        return EMPTY

