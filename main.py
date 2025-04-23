import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml

class Parser:
    def __init__(self):
        self.url = 'https://fedast.ru/sitemap.xml'

    
    # def collect_all_pages(self):

    #     response = requests.get(url=self.url)
    #     response.encoding = 'utf-8'
    #     soup = BeautifulSoup(response.text, 'xml')

    #     urls = soup.find_all("loc")
    #     product_urls = [url.text for url in urls if url.text.startswith("https://fedast.ru/product/")]

    #     return product_urls


    def parsing_products(self):

        # all_pages = self.collect_all_pages()


        response = requests.get(url='https://fedast.ru/product/zapchast-75-dlya-hybest-gsr40a-prokladka-dlya-zazhima-ballona')
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'lxml')

        url = 'pass'
        category = ' > '.join([
            item.strip() 
            for item in soup.select_one('.breadcrumb-wrapper').text.strip().split('\n') 
            if item.strip() != '' and item.strip() != '...'
        ])
        image = soup.select_one('.img-ratio.img-fit.product__photo').get('href')


        title = soup.select_one('.product-form__area-title').text.strip()
        article = soup.select_one('div.product__sku span.sku-value')
        main_description = soup.select_one(".product__short-description.static-text").text.strip()
        price = soup.select_one('.product__price').text
        description = soup.select_one('.product-description.static-text').text.strip()
        property = {k.text:v.text.strip() for k,v in zip(soup.select('.property__name'), soup.select('.property__content'))}


        return category
            

   

parser = Parser()
print(parser.parsing_products())






