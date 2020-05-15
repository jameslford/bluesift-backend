import requests
from bs4 import BeautifulSoup


def scrape():
    for num in range(1, 5):
        URL = f"https://www.porcelanosa-usa.com/products/tile?cat=6&colors=1308%2C1441%2C1509%2C1310%2C643%2C644%2C645%2C646%2C647%2C648%2C650%2C651&p={num}&product_list_limit=100"
        res = requests.get(url=URL).text
        soup = BeautifulSoup(res, "lxml")
        olist = soup.find("ol", class_="products")
        # print(olist)
        prods = olist.findAll("li")
        for prod in prods:
            link = prod.find("a")
            print(link["href"])
