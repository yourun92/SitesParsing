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
        self.url = 'https://fedast.ru/sitemap.xml'
        self.data = []
        self.ind = 0
        self.ua = UserAgent()
        
    
    def collect_all_pages(self):

        response = requests.get(url=self.url)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'xml')

        urls = soup.find_all("loc")
        product_urls = [url.text for url in urls if url.text.startswith("https://fedast.ru/product/")]

        return product_urls


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
                category = ' > '.join([
                    item.strip() 
                    for item in soup.select_one('.breadcrumb-wrapper').text.strip().split('\n') 
                    if item.strip() != '' and item.strip() != '...'
                ])
                
                image_tag = soup.select_one('.img-ratio.img-fit.product__photo')
                if not image_tag:
                    image_tag = soup.select_one('.img-ratio.img-ratio_cover.product__photo')
                image = image_tag.get('href') if image_tag else ''

                title = soup.select_one('.product-form__area-title')
                title = title.text.strip() if title else ''
                article = soup.select_one('div.product__sku span.sku-value')
                
                main_description = soup.select_one(".product__short-description.static-text")
                main_description = main_description.text.strip() if main_description else ''
                
                price = soup.select_one('.product__price')
                price = price.text.strip() if price else ''
                
                description = soup.select_one('.product-description.static-text')
                description = description.text.strip() if description else ''
                
                properties = {k.text:v.text.strip() for k,v in zip(soup.select('.property__name'), soup.select('.property__content'))}

                # Объединяем основные поля и свойства
                product_data = {
                    'url': url,
                    'category': category,
                    'image': image,
                    'title': title,
                    'article': article,
                    'main_description': main_description,
                    'price': price,
                    'description': description,
                }

                product_data.update(properties)
                self.data.append(product_data)

                self.ind += 1
                if self.ind % 100 == 0:
                    print(f'Обработано {self.ind} страниц')

                # Случайная задержка между запросами
                time.sleep(random.uniform(1, 3))

                # Сохраняем промежуточные результаты
                if self.ind % 100 == 0:
                    df = pd.DataFrame(self.data)
                    df.to_excel(f"fedast_interim_{self.ind}.xlsx", index=False)

            except Exception as e:
                print(f"Ошибка при обработке {url}: {e}")
                continue

            

   

parser = Parser()
parser.parsing_products()


df = pd.DataFrame(parser.data)
df.to_excel('fedast.xlsx', index=False)






