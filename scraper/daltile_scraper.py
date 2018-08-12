from selenium import webdriver 
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import html5lib
import csv
import time
import os
import re


def run(page_number=0):

    url = 'https://www.daltile.com/products'
    driver = webdriver.Chrome()
    driver.get(url)
    path = os.getcwd()
    f = path + "\\daltile-list2.txt"
    applications = []
    finishes = []
    page_counter = 0

    while page_counter < page_number:
        try:
            element = WebDriverWait(driver, 100).until(
                EC.invisibility_of_element_located((By.ID, "loadingContent"))
                )
            print(page_counter)
        finally:
            pass
        time.sleep(2)
        soup_level1 = BeautifulSoup(driver.page_source, 'html5lib')
        for link in soup_level1.find_all('a','product-url'):

            def get_application():
                app = str(link.find(class_= 'section__item--subheading').contents[0])
                if app:
                    return app.strip().split('\\')
                else:
                    return 'N/A'


            def get_finish():
                fins = str(link.find(class_='section__item--subheading last').contents).strip().replace('\\n','').strip()
                if fins:
                    for ch in ["['","']",'\\n','u200b/', '\\u200b']:
                        fins = fins.replace(ch,'')
                    
                    return fins.strip().split('\\')
                else:
                    return 'N/A'

            product_name = str(link.find(class_= 'section__item--heading').contents[0]).strip()
            image_url = str(link.find(class_= 'product-thumb')['src']).strip()
            product_url = str(link.get('href'))
            application = get_application()
            finish = get_finish()
        
            applications.append(application)
            finishes.append(finish)

            


            line = '["' + product_name + '", "' + image_url + '", "' + application + '", "'+ finish + '", "' + product_url + '"], ' 

            with open(f,'a+') as txtfile:
            
                try:
                    print(line, file=txtfile)
                except:
                    print('["error"], ', file=txtfile)
        
            

        button = driver.find_element_by_xpath("//img[@src='/Assets/Daltile/Images/pagination-right.png']")
        button.click()
        page_counter += 1

    finish_set1 = set(finishes)
    application_set1 = set(applications)

    finish_list = []
    for finish in finish_set1:
        if '\\' in finish:
            split = finish.split('\\')
            for s in split:
                finish_list.append(s)
        else:
            finish_list.append(finish)

    finish_set2 = set(finish_list)
    print(finish_set2)