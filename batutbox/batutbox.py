import pandas as pd
import requests
import lxml
from bs4 import BeautifulSoup
import xml
import time
import random
from fake_useragent import UserAgent

class Parser:
    def __init__(self):
        self.url = 'https://batutbox.ru/product-sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()
        
    
    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        urls = soup.find_all("loc")
        product_urls = [url.text for url in urls]

        return product_urls[1:]

    def parsing_products(self):

        product_urls = self.collect_all_pages()

        for url in product_urls:
            try:
                headers = {
                    'User-Agent': self.ua.random,
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8',
                    'Connection': 'keep-alive'
                }

                response = requests.get(url=url, headers=headers, timeout=30)
                response.encoding = 'utf-8'
                soup = BeautifulSoup(response.text, 'lxml')

                url = url

                category = soup.select_one('.site.grid-container.container.hfeed').select_one('.woocommerce-breadcrumb')
                category = ' > '.join(category.text.strip().split('|')) if category else ''
                
                image_tag = soup.select_one('.rtwpvg-single-image-container').select_one('img')
                image = image_tag.get('data-large_image')

                title = soup.select_one('.summary.entry-summary').select_one('h1')
                title = title.text.strip() if title else ''
            #     article = soup.select_one('div.product__sku span.sku-value')
                
                # main_description = soup.select_one(".product__short-description.static-text")
                # main_description = main_description.text.strip() if main_description else ''
                
            #     price = soup.select_one('.product__price')
            #     price = price.text.strip() if price else ''
                
                description = soup.select_one('.singltovaropisanie-name')
                description = description.text.strip() if description else ''
                
                properties = soup.select_one('.atrtovarpodzag').select('p')
                properties = {k.strip():v.strip() for k,v in [p.text.split(':') for p in properties]} if properties else ''

                # Объединяем основные поля и свойства
                product_data = {
                    'url': url,
                    'category': category,
                    'image': image,
                    'title': title,
                    'description': description,
                }

                product_data.update(properties)
                self.data.append(product_data)

                self.ind += 1
                if self.ind % 10 == 0:
                    print(f'Обработано {self.ind} страниц')

                # Случайная задержка между запросами
                time.sleep(random.uniform(1, 3))

            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue

   

parser = Parser()
print(parser.parsing_products())


df = pd.DataFrame(parser.data)
df.to_excel('batutbox.xlsx', index=False)






